"""
Document Processing Routes
Endpoints for file and URL processing
"""

import json
import shutil
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse

from app.api.models.requests import ProcessFileRequest, ProcessUrlRequest
from app.api.models.responses import ProcessingStatus
from app.services.job_service import (
    create_job, get_job, delete_job, get_result_file_path, UPLOAD_DIR
)
from app.services.document_service import DocumentProcessingService

router = APIRouter()


@router.post("/file", response_model=ProcessingStatus)
async def process_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    config: str = '{"output_format": "documents"}'
):
    """Process uploaded file"""
    try:
        # Parse configuration
        config_data = json.loads(config)
        
        # Create job
        job_id = create_job("file", config_data)
        
        # Save uploaded file
        file_path = UPLOAD_DIR / f"{job_id}_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Update job with file path
        job_data = get_job(job_id)
        job_data["file_path"] = str(file_path)
        
        # Start background processing
        background_tasks.add_task(
            DocumentProcessingService.process_file, 
            job_id, 
            str(file_path), 
            config_data
        )
        
        job_data = get_job(job_id)
        return ProcessingStatus(**job_data)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")


@router.post("/url", response_model=ProcessingStatus)
async def process_url(background_tasks: BackgroundTasks, request: ProcessUrlRequest):
    """Process URL"""
    try:
        # Create job
        job_id = create_job("url", request.dict())
        
        # Update job with URL
        job_data = get_job(job_id)
        job_data["url"] = str(request.url)
        
        # Start background processing
        background_tasks.add_task(
            DocumentProcessingService.process_url,
            job_id, 
            str(request.url), 
            request.dict()
        )
        
        job_data = get_job(job_id)
        return ProcessingStatus(**job_data)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing URL: {str(e)}")


@router.get("/{job_id}", response_model=ProcessingStatus)
async def get_job_status(job_id: str):
    """Get job status"""
    job_data = get_job(job_id)
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return ProcessingStatus(**job_data)


@router.get("/{job_id}/download")
async def download_result(job_id: str):
    """Download processed results"""
    job_data = get_job(job_id)
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job_data["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")
    
    output_file = get_result_file_path(job_id)
    if not output_file.exists():
        raise HTTPException(status_code=404, detail="Result file not found")
    
    # Return JSON data directly instead of file download
    with open(output_file, 'r') as f:
        result_data = json.load(f)
    
    return JSONResponse(content=result_data)


@router.delete("/{job_id}")
async def cleanup_job(job_id: str):
    """Clean up job files and data"""
    if not delete_job(job_id):
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"message": "Job cleaned up successfully"}