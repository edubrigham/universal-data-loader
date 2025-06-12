"""
API Response Models
Pydantic models for API responses
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


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


class Link(BaseModel):
    """A HATEOAS link."""
    rel: str = Field(..., description="Relation type of the link.")
    href: str = Field(..., description="The target URL of the link.")


class JobCreated(BaseModel):
    """Response model for when a job is successfully created."""
    job_id: str = Field(..., description="The unique identifier for the job.")
    status: str = Field(..., description="The initial status of the job, e.g., 'pending'.")
    links: List[Link] = Field(..., description="Links to the job status and results.")


class JobStatus(BaseModel):
    """Response model for the status of a job."""
    job_id: str
    status: str
    error: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None
    links: List[Link] = []


class Document(BaseModel):
    """A single processed document, compatible with LangChain."""
    page_content: str
    metadata: Dict[str, Any]


class JobResult(BaseModel):
    """Response model for the final result of a completed job."""
    job_id: str
    documents: List[Document]