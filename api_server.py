#!/usr/bin/env python3
"""
Universal Data Loader API Server
Containerized REST API for document processing
"""

import os
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, HttpUrl
import uvicorn

from universal_loader import UniversalDataLoader, BatchProcessor
from universal_loader.config import LoaderConfig, OutputFormat, ChunkingStrategy
from universal_loader.batch_config import BatchConfig, InputSource, InputType, OutputConfig
from universal_loader.document import DocumentCollection


# API Models
class ProcessFileRequest(BaseModel):
    """Request model for file processing"""
    output_format: Optional[str] = "documents"
    chunking_strategy: Optional[str] = None
    max_chunk_size: Optional[int] = 1000
    chunk_overlap: Optional[int] = 100
    include_metadata: Optional[bool] = True
    min_text_length: Optional[int] = 10
    remove_headers_footers: Optional[bool] = True
    ocr_languages: Optional[List[str]] = ["eng"]


class ProcessUrlRequest(BaseModel):
    """Request model for URL processing"""
    url: HttpUrl
    output_format: Optional[str] = "documents"
    chunking_strategy: Optional[str] = None
    max_chunk_size: Optional[int] = 1000
    chunk_overlap: Optional[int] = 100
    include_metadata: Optional[bool] = True
    min_text_length: Optional[int] = 10
    remove_headers_footers: Optional[bool] = True


class BatchProcessRequest(BaseModel):
    """Request model for batch processing"""
    sources: List[Dict[str, Any]]
    loader_config: Optional[Dict[str, Any]] = {}
    output_config: Optional[Dict[str, Any]] = {
        "separate_by_source": True,
        "merge_all": False
    }
    max_workers: Optional[int] = 3
    continue_on_error: Optional[bool] = True


class ProcessingStatus(BaseModel):
    """Response model for processing status"""
    job_id: str
    status: str  # "pending", "processing", "completed", "failed"
    created_at: str
    completed_at: Optional[str] = None
    documents_count: Optional[int] = None
    error_message: Optional[str] = None
    download_url: Optional[str] = None


# Initialize FastAPI app
app = FastAPI(
    title="Universal Data Loader API",
    description="Containerized document processing service for LLM applications",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Global storage for job tracking
jobs_storage = {}
UPLOAD_DIR = Path("/tmp/uploads")
OUTPUT_DIR = Path("/tmp/outputs")

# Ensure directories exist
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


def create_loader_config(request_data: Dict[str, Any]) -> LoaderConfig:
    """Create LoaderConfig from request data"""
    config_dict = {
        "output_format": OutputFormat(request_data.get("output_format", "documents")),
        "include_metadata": request_data.get("include_metadata", True),
        "max_chunk_size": request_data.get("max_chunk_size", 1000),
        "chunk_overlap": request_data.get("chunk_overlap", 100),
        "min_text_length": request_data.get("min_text_length", 10),
        "remove_headers_footers": request_data.get("remove_headers_footers", True),
        "ocr_languages": request_data.get("ocr_languages", ["eng"])
    }
    
    if request_data.get("chunking_strategy"):
        config_dict["chunking_strategy"] = ChunkingStrategy(request_data["chunking_strategy"])
    
    return LoaderConfig(**config_dict)


def generate_job_id() -> str:
    """Generate unique job ID"""
    return f"job_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}"


def update_job_status(job_id: str, status: str, **kwargs):
    """Update job status in storage"""
    if job_id in jobs_storage:
        jobs_storage[job_id]["status"] = status
        jobs_storage[job_id].update(kwargs)
        if status in ["completed", "failed"]:
            jobs_storage[job_id]["completed_at"] = datetime.now().isoformat()


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "Universal Data Loader API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "process_file": "/process/file",
            "process_url": "/process/url", 
            "batch_process": "/process/batch",
            "job_status": "/jobs/{job_id}",
            "download": "/download/{job_id}",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": "running",
        "active_jobs": len([j for j in jobs_storage.values() if j["status"] == "processing"])
    }


@app.post("/process/file", response_model=ProcessingStatus)
async def process_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    config: str = '{"output_format": "documents"}'
):
    """Process uploaded file"""
    try:
        # Parse configuration
        config_data = json.loads(config)
        
        # Generate job ID
        job_id = generate_job_id()
        
        # Save uploaded file
        file_path = UPLOAD_DIR / f"{job_id}_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create job record
        jobs_storage[job_id] = {
            "job_id": job_id,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "file_path": str(file_path),
            "config": config_data
        }
        
        # Start background processing
        background_tasks.add_task(process_file_background, job_id, str(file_path), config_data)
        
        return ProcessingStatus(
            job_id=job_id,
            status="pending",
            created_at=jobs_storage[job_id]["created_at"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")


@app.post("/process/url", response_model=ProcessingStatus)
async def process_url(background_tasks: BackgroundTasks, request: ProcessUrlRequest):
    """Process URL"""
    try:
        # Generate job ID
        job_id = generate_job_id()
        
        # Create job record
        jobs_storage[job_id] = {
            "job_id": job_id,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "url": str(request.url),
            "config": request.dict()
        }
        
        # Start background processing
        background_tasks.add_task(process_url_background, job_id, str(request.url), request.dict())
        
        return ProcessingStatus(
            job_id=job_id,
            status="pending", 
            created_at=jobs_storage[job_id]["created_at"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing URL: {str(e)}")


@app.post("/process/batch", response_model=ProcessingStatus)
async def batch_process(background_tasks: BackgroundTasks, request: BatchProcessRequest):
    """Process multiple sources in batch"""
    try:
        # Generate job ID
        job_id = generate_job_id()
        
        # Create job record
        jobs_storage[job_id] = {
            "job_id": job_id,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "config": request.dict()
        }
        
        # Start background processing
        background_tasks.add_task(process_batch_background, job_id, request.dict())
        
        return ProcessingStatus(
            job_id=job_id,
            status="pending",
            created_at=jobs_storage[job_id]["created_at"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error starting batch process: {str(e)}")


@app.get("/jobs/{job_id}", response_model=ProcessingStatus)
async def get_job_status(job_id: str):
    """Get job status"""
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_data = jobs_storage[job_id]
    return ProcessingStatus(**job_data)


@app.get("/download/{job_id}")
async def download_result(job_id: str):
    """Download processed results"""
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_data = jobs_storage[job_id]
    if job_data["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")
    
    output_file = OUTPUT_DIR / f"{job_id}_result.json"
    if not output_file.exists():
        raise HTTPException(status_code=404, detail="Result file not found")
    
    return FileResponse(
        path=str(output_file),
        filename=f"{job_id}_result.json",
        media_type="application/json"
    )


@app.delete("/jobs/{job_id}")
async def cleanup_job(job_id: str):
    """Clean up job files and data"""
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Remove from storage
    job_data = jobs_storage.pop(job_id)
    
    # Clean up files
    if "file_path" in job_data:
        file_path = Path(job_data["file_path"])
        if file_path.exists():
            file_path.unlink()
    
    output_file = OUTPUT_DIR / f"{job_id}_result.json"
    if output_file.exists():
        output_file.unlink()
    
    return {"message": "Job cleaned up successfully"}


async def process_file_background(job_id: str, file_path: str, config: Dict[str, Any]):
    """Background task for file processing"""
    try:
        update_job_status(job_id, "processing")
        
        # Create loader and process
        loader_config = create_loader_config(config)
        loader = UniversalDataLoader(loader_config)
        documents = loader.load_file(file_path)
        
        # Save results
        output_file = OUTPUT_DIR / f"{job_id}_result.json"
        loader.save_output(documents, output_file)
        
        # Update job status
        stats = documents.get_statistics()
        update_job_status(
            job_id, 
            "completed",
            documents_count=stats["document_count"],
            download_url=f"/download/{job_id}"
        )
        
    except Exception as e:
        update_job_status(job_id, "failed", error_message=str(e))
    
    finally:
        # Clean up uploaded file
        Path(file_path).unlink(missing_ok=True)


async def process_url_background(job_id: str, url: str, config: Dict[str, Any]):
    """Background task for URL processing"""
    try:
        update_job_status(job_id, "processing")
        
        # Create loader and process
        loader_config = create_loader_config(config)
        loader = UniversalDataLoader(loader_config)
        documents = loader.load_url(url)
        
        # Save results
        output_file = OUTPUT_DIR / f"{job_id}_result.json"
        loader.save_output(documents, output_file)
        
        # Update job status
        stats = documents.get_statistics()
        update_job_status(
            job_id,
            "completed", 
            documents_count=stats["document_count"],
            download_url=f"/download/{job_id}"
        )
        
    except Exception as e:
        update_job_status(job_id, "failed", error_message=str(e))


async def process_batch_background(job_id: str, config: Dict[str, Any]):
    """Background task for batch processing"""
    try:
        update_job_status(job_id, "processing")
        
        # Create batch configuration
        sources = []
        for source_data in config["sources"]:
            source = InputSource(**source_data)
            sources.append(source)
        
        batch_config = BatchConfig(
            sources=sources,
            loader_config=LoaderConfig(**config.get("loader_config", {})),
            output=OutputConfig(
                base_path=str(OUTPUT_DIR / job_id),
                **config.get("output_config", {})
            ),
            max_workers=config.get("max_workers", 3),
            continue_on_error=config.get("continue_on_error", True)
        )
        
        # Process batch
        processor = BatchProcessor(batch_config)
        results = processor.process_all()
        
        # Save summary
        output_file = OUTPUT_DIR / f"{job_id}_result.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Update job status
        update_job_status(
            job_id,
            "completed",
            documents_count=results["total_documents"],
            download_url=f"/download/{job_id}"
        )
        
    except Exception as e:
        update_job_status(job_id, "failed", error_message=str(e))


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "api_server:app",
        host=host,
        port=port,
        reload=False,
        access_log=True
    )