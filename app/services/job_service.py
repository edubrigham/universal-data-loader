"""
Job Management Service
Handles job creation, tracking, and status management
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

# Global storage for job tracking (in production, this would be Redis/Database)
jobs_storage: Dict[str, Dict[str, Any]] = {}

# Directories for job processing
UPLOAD_DIR = Path("/tmp/uploads")
OUTPUT_DIR = Path("/tmp/outputs")

# Ensure directories exist
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


def generate_job_id() -> str:
    """Generate unique job ID"""
    return f"job_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}"


def create_job(job_type: str, config: Dict[str, Any], **kwargs) -> str:
    """Create a new job and return job ID"""
    job_id = generate_job_id()
    
    job_data = {
        "job_id": job_id,
        "job_type": job_type,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "config": config,
        **kwargs
    }
    
    jobs_storage[job_id] = job_data
    return job_id


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    """Get job by ID"""
    return jobs_storage.get(job_id)


def update_job_status(job_id: str, status: str, **kwargs):
    """Update job status in storage"""
    if job_id in jobs_storage:
        jobs_storage[job_id]["status"] = status
        jobs_storage[job_id].update(kwargs)
        if status in ["completed", "failed"]:
            jobs_storage[job_id]["completed_at"] = datetime.now().isoformat()


def delete_job(job_id: str) -> bool:
    """Delete job and return success status"""
    if job_id in jobs_storage:
        job_data = jobs_storage.pop(job_id)
        
        # Clean up files
        if "file_path" in job_data:
            file_path = Path(job_data["file_path"])
            if file_path.exists():
                file_path.unlink()
        
        output_file = OUTPUT_DIR / f"{job_id}_result.json"
        if output_file.exists():
            output_file.unlink()
        
        return True
    return False


def get_active_jobs_count() -> int:
    """Get count of active jobs"""
    return len([j for j in jobs_storage.values() if j["status"] == "processing"])


def get_result_file_path(job_id: str) -> Path:
    """Get the result file path for a job"""
    return OUTPUT_DIR / f"{job_id}_result.json"