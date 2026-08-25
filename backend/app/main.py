import sys
import asyncio
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
from contextlib import asynccontextmanager
from hmac import compare_digest

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import scholarships_router, sources_router
from app.config.settings import settings
from app.services.scheduler.discovery_job import (
    DiscoveryAlreadyRunning,
    run_scheduled_discovery,
)

# Instantiate the APScheduler object
scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP: Register discovery job to run every N hours
    scheduler.add_job(
        run_scheduled_discovery,
        trigger="interval",
        hours=settings.SCHEDULER_INTERVAL_HOURS,
        id="scheduled_scholarship_discovery",
        replace_existing=True,
    )
    scheduler.start()
    print(f"=== APScheduler Started: Running discovery every {settings.SCHEDULER_INTERVAL_HOURS} hours ===")
    
    yield
    
    # SHUTDOWN: Gracefully stop scheduler
    scheduler.shutdown()
    print("=== APScheduler Stopped cleanly ===")


app = FastAPI(
    title="ScholarScout AI API",
    version="1.0.0",
    lifespan=lifespan,
)

# Combine configured origins from settings with localhost:3000
origins = [
    origin.strip()
    for origin in settings.FRONTEND_ORIGINS.split(",")
    if origin.strip()
]
if "http://localhost:3000" not in origins:
    origins.append("http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Admin-Key"],
)

app.include_router(scholarships_router, prefix="/api/v1")
app.include_router(sources_router, prefix="/api/v1")


@app.get("/api/v1/")
def root():
    return {"status": "ok", "message": "ScholarScout AI backend is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/admin/discovery/run")
async def manual_discovery(x_admin_key: str | None = Header(default=None)):
    """Run discovery manually; production requires the configured admin key."""
    configured_key = settings.ADMIN_API_KEY
    if configured_key:
        if not x_admin_key or not compare_digest(x_admin_key, configured_key):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid admin API key",
            )
    elif settings.APP_ENV.lower() == "production":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ADMIN_API_KEY must be configured in production",
        )

    try:
        await run_scheduled_discovery()
    except DiscoveryAlreadyRunning as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A discovery run is already in progress",
        ) from exc

    return {"status": "completed", "message": "Scholarship discovery completed"}