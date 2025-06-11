"""
API Response Models
Pydantic models for API responses
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel


class ProcessingStatus(BaseModel):
    """Response model for processing status"""
    job_id: str
    status: str  # "pending", "processing", "completed", "failed"
    created_at: str
    completed_at: Optional[str] = None
    documents_count: Optional[int] = None
    error_message: Optional[str] = None
    download_url: Optional[str] = None


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    timestamp: str
    uptime: str
    active_jobs: int


class ServiceInfoResponse(BaseModel):
    """Response model for service information"""
    service: str
    version: str
    status: str
    endpoints: Dict[str, str]


class ErrorResponse(BaseModel):
    """Response model for error responses"""
    error: str
    message: str
    detail: Optional[str] = None