from fastapi import FastAPI

app = FastAPI(
    title="ScholarScout AI",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "ScholarScout AI backend is running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }