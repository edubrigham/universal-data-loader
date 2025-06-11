"""
API Request Models
Pydantic models for validating incoming requests
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, HttpUrl, validator


class ProcessFileRequest(BaseModel):
    """Request model for file processing"""
    output_format: Optional[str] = "documents"
    enable_chunking: Optional[bool] = False
    chunking_strategy: Optional[str] = None  # Required if enable_chunking=True
    max_chunk_size: Optional[int] = None     # Required if enable_chunking=True
    chunk_overlap: Optional[int] = None      # Optional when chunking
    include_metadata: Optional[bool] = True
    min_text_length: Optional[int] = 10
    remove_headers_footers: Optional[bool] = True
    ocr_languages: Optional[List[str]] = ["eng"]
    
    @validator('chunking_strategy')
    def validate_chunking_strategy(cls, v, values):
        if values.get('enable_chunking') and not v:
            raise ValueError('chunking_strategy is required when enable_chunking=True')
        return v
    
    @validator('max_chunk_size')
    def validate_max_chunk_size(cls, v, values):
        if values.get('enable_chunking') and not v:
            raise ValueError('max_chunk_size is required when enable_chunking=True')
        return v


class ProcessUrlRequest(BaseModel):
    """Request model for URL processing"""
    url: HttpUrl
    output_format: Optional[str] = "documents"
    enable_chunking: Optional[bool] = False
    chunking_strategy: Optional[str] = None  # Required if enable_chunking=True
    max_chunk_size: Optional[int] = None     # Required if enable_chunking=True
    chunk_overlap: Optional[int] = None      # Optional when chunking
    include_metadata: Optional[bool] = True
    min_text_length: Optional[int] = 10
    remove_headers_footers: Optional[bool] = True
    
    @validator('chunking_strategy')
    def validate_chunking_strategy(cls, v, values):
        if values.get('enable_chunking') and not v:
            raise ValueError('chunking_strategy is required when enable_chunking=True')
        return v
    
    @validator('max_chunk_size')
    def validate_max_chunk_size(cls, v, values):
        if values.get('enable_chunking') and not v:
            raise ValueError('max_chunk_size is required when enable_chunking=True')
        return v


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