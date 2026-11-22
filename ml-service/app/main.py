from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="Knowledge Tracing and Adaptive Recommendation Engine for Personalized Study Planning",
    version="0.1.0",
)

# Configure CORS for development origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["System"])
async def health_check():
    """Service health status endpoint."""
    return {
        "status": "healthy",
        "service": "ml-service",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

@app.get("/", tags=["System"])
async def root():
    """Root entrypoint providing service status."""
    return {
        "message": "Adaptive Study Planner - Machine Learning Service",
        "documentation": "/docs",
        "phase": "Phase 2 - Foundation",
    }
