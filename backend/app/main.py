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
from app.services.scheduler.service import scheduler_instance

from app.services.scheduler.discovery_job import (
    DiscoveryAlreadyRunning,
    run_scheduled_discovery,
)

# Instantiate the APScheduler object
scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize background scheduler engine
    print("⏰ Starting background ScholarshipScheduler...")
    scheduler_instance.start()
    yield
    # Shutdown: Clean up scheduler threads
    print("🛑 Shutting down background ScholarshipScheduler...")
    scheduler_instance.shutdown()


app = FastAPI(
    title="ScholarScout AI API",
    version="1.0.0",
    lifespan=lifespan,
)

# Register API routers cleanly
app.include_router(scholarships_router, prefix="/api/v1")
app.include_router(sources_router, prefix="/api/v1")

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