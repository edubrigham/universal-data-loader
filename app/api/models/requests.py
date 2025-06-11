"""
API Request Models
Pydantic models for validating incoming requests
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, HttpUrl


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