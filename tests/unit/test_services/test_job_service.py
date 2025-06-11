"""
Unit Tests for Job Service
"""

import pytest
from app.services.job_service import (
    generate_job_id, create_job, get_job, update_job_status, 
    delete_job, get_active_jobs_count
)


def test_generate_job_id():
    """Test job ID generation"""
    job_id = generate_job_id()
    assert job_id.startswith("job_")
    assert len(job_id) > 10


def test_create_job():
    """Test job creation"""
    config = {"test": "value"}
    job_id = create_job("test", config)
    
    job = get_job(job_id)
    assert job is not None
    assert job["job_id"] == job_id
    assert job["job_type"] == "test"
    assert job["status"] == "pending"
    assert job["config"] == config


def test_update_job_status():
    """Test job status updates"""
    job_id = create_job("test", {})
    
    update_job_status(job_id, "processing")
    job = get_job(job_id)
    assert job["status"] == "processing"
    
    update_job_status(job_id, "completed", documents_count=5)
    job = get_job(job_id)
    assert job["status"] == "completed"
    assert job["documents_count"] == 5
    assert "completed_at" in job


def test_delete_job():
    """Test job deletion"""
    job_id = create_job("test", {})
    assert get_job(job_id) is not None
    
    result = delete_job(job_id)
    assert result is True
    assert get_job(job_id) is None


def test_get_active_jobs_count():
    """Test active jobs counting"""
    # Create some jobs
    job1 = create_job("test1", {})
    job2 = create_job("test2", {})
    job3 = create_job("test3", {})
    
    # Mark some as processing
    update_job_status(job1, "processing")
    update_job_status(job2, "processing")
    update_job_status(job3, "completed")
    
    assert get_active_jobs_count() == 2