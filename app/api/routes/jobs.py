"""
Unified Job-Based Routes
Endpoints for creating and managing all processing jobs, conforming to the OpenAPI spec.
"""

import json
import shutil
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks, status, Request, Depends
from fastapi.responses import JSONResponse

from app.api.models.requests import ProcessUrlRequest, BatchProcessRequest
from app.api.models.responses import JobCreated, JobStatus, JobResult
from app.core.security import get_api_key
from app.services.job_service import (
    create_job, get_job, delete_job, get_result_file_path, UPLOAD_DIR
)
from app.services.document_service import DocumentProcessingService

router = APIRouter()

def _create_job_links(job_id: str, request: Request) -> list:
    """Creates HATEOAS links for a job."""
    base_url = str(request.base_url)
    api_root = f"api/v1/jobs/{job_id}"
    return [
        {"rel": "status", "href": f"{base_url}{api_root}"},
        {"rel": "result", "href": f"{base_url}{api_root}/result"},
    ]

@router.post(
    "/file", 
    response_model=JobCreated, 
    status_code=status.HTTP_202_ACCEPTED,
    summary="Process a single file",
    dependencies=[Depends(get_api_key)]
)
async def process_file(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    config: str = '{"output_format": "documents"}'
):
    """
    Upload a single file for processing.
    
    This endpoint is ideal for on-the-fly processing of individual documents.
    The file is processed asynchronously. Use the returned `job_id` to check status
    and retrieve results.
    """
    try:
        config_data = json.loads(config)
        job_id = create_job("file", config_data)
        
        file_path = UPLOAD_DIR / f"{job_id}_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        job_data = get_job(job_id)
        job_data["file_path"] = str(file_path)
        
        background_tasks.add_task(
            DocumentProcessingService.process_file, job_id, str(file_path), config_data
        )
        
        return JobCreated(
            job_id=job_id,
            status=get_job(job_id).get("status", "pending"),
            links=_create_job_links(job_id, request)
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post(
    "/url",
    response_model=JobCreated,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Process a single URL",
    dependencies=[Depends(get_api_key)]
)
async def process_url(request: Request, background_tasks: BackgroundTasks, url_request: ProcessUrlRequest):
    """
    Process a document from a single URL.
    
    The document at the URL is downloaded and processed asynchronously. Use the
    returned `job_id` to check status and retrieve results.
    """
    try:
        job_id = create_job("url", url_request.dict())
        job_data = get_job(job_id)
        job_data["url"] = str(url_request.url)
        
        background_tasks.add_task(
            DocumentProcessingService.process_url, job_id, str(url_request.url), url_request.dict()
        )
        
        return JobCreated(
            job_id=job_id,
            status=get_job(job_id).get("status", "pending"),
            links=_create_job_links(job_id, request)
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post(
    "/batch",
    response_model=JobCreated,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Process a batch of sources",
    dependencies=[Depends(get_api_key)]
)
async def batch_process(request: Request, background_tasks: BackgroundTasks, batch_request: BatchProcessRequest):
    """
    Process multiple sources (files, URLs, directories) in a single batch job.
    
    This is the most powerful endpoint, designed for bulk processing based on a
    configuration similar to `config/documents.json`. The job runs asynchronously.
    """
    try:
        job_id = create_job("batch", batch_request.dict())
        background_tasks.add_task(
            DocumentProcessingService.process_batch, job_id, batch_request.dict()
        )
        
        return JobCreated(
            job_id=job_id,
            status=get_job(job_id).get("status", "pending"),
            links=_create_job_links(job_id, request)
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get(
    "/{job_id}",
    response_model=JobStatus,
    summary="Get job status"
)
async def get_job_status(job_id: str, request: Request):
    """
    Retrieve the current status of a processing job.
    
    Status can be `pending`, `processing`, `completed`, or `failed`.
    """
    job_data = get_job(job_id)
    if not job_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    
    # Add links to the response
    job_data_with_links = {**job_data, "links": _create_job_links(job_id, request)}
    return JobStatus(**job_data_with_links)

@router.get(
    "/{job_id}/result",
    response_model=JobResult,
    summary="Get job result"
)
async def get_job_result(job_id: str):
    """
    Retrieve the result of a completed job.
    
    This returns the final, processed documents in LangChain-compatible format.
    """
    job_data = get_job(job_id)
    if not job_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    
    if job_data["status"] != "completed":
        # Return a 202 Accepted response with the current status
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content=JobStatus(**job_data).dict()
        )
    
    output_file = get_result_file_path(job_id)
    if not output_file.exists():
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Result file not found")
    
    with open(output_file, 'r') as f:
        result_data = json.load(f)
    
    return JobResult(job_id=job_id, documents=result_data)

@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a job",
    dependencies=[Depends(get_api_key)]
)
async def cleanup_job(job_id: str):
    """
    Clean up a job and its associated files from the server.
    
    This is an optional step to free up disk space.
    """
    if not delete_job(job_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    
    return None # No content 