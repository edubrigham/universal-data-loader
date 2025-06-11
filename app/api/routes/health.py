"""
Health Check Routes
Service health monitoring and status endpoints
"""

from datetime import datetime
from fastapi import APIRouter
from app.api.models.responses import HealthResponse, ServiceInfoResponse

# Import jobs storage from services layer
from app.services.job_service import get_active_jobs_count

router = APIRouter()


@router.get("/", response_model=ServiceInfoResponse)
async def root():
    """Root endpoint with API information"""
    return ServiceInfoResponse(
        service="Universal Data Loader API",
        version="1.0.0",
        status="running",
        endpoints={
            "health": "/health",
            "process_file": "/process/file",
            "process_url": "/process/url", 
            "batch_process": "/process/batch",
            "job_status": "/jobs/{job_id}",
            "download": "/download/{job_id}",
            "docs": "/docs"
        }
    )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        uptime="running",
        active_jobs=get_active_jobs_count()
    )