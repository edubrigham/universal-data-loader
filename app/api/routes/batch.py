"""
Batch Processing Routes
Endpoints for batch document processing
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks

from app.api.models.requests import BatchProcessRequest
from app.api.models.responses import ProcessingStatus
from app.services.job_service import create_job, get_job
from app.services.document_service import DocumentProcessingService

router = APIRouter()


@router.post("/batch", response_model=ProcessingStatus)
async def batch_process(background_tasks: BackgroundTasks, request: BatchProcessRequest):
    """Process multiple sources in batch"""
    try:
        # Create job
        job_id = create_job("batch", request.dict())
        
        # Start background processing
        background_tasks.add_task(
            DocumentProcessingService.process_batch,
            job_id, 
            request.dict()
        )
        
        job_data = get_job(job_id)
        return ProcessingStatus(**job_data)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error starting batch process: {str(e)}")