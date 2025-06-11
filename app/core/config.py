"""
Configuration classes for the Universal Data Loader
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


class OutputFormat(str, Enum):
    JSON = "json"
    TEXT = "text"
    ELEMENTS = "elements"
    DOCUMENTS = "documents"  # LangChain-compatible Document objects


class ChunkingStrategy(str, Enum):
    BASIC = "basic"
    BY_TITLE = "by_title"
    BY_PAGE = "by_page"
    BY_SIMILARITY = "by_similarity"


class LoaderConfig(BaseModel):
    """Configuration for the Universal Data Loader"""
    
    # Output settings
    output_format: OutputFormat = Field(default=OutputFormat.DOCUMENTS, description="Format for output data")
    include_metadata: bool = Field(default=True, description="Whether to include metadata in output")
    
    # Processing settings
    chunking_strategy: Optional[ChunkingStrategy] = Field(default=None, description="Strategy for chunking documents")
    max_chunk_size: int = Field(default=1000, description="Maximum size of text chunks")
    chunk_overlap: int = Field(default=100, description="Overlap between chunks")
    
    # File processing
    ocr_languages: List[str] = Field(default=["eng"], description="Languages for OCR processing")
    extract_images: bool = Field(default=False, description="Whether to extract images from documents")
    
    # Content filtering
    min_text_length: int = Field(default=10, description="Minimum text length to include")
    remove_headers_footers: bool = Field(default=True, description="Remove headers and footers")
    
    # Advanced settings
    custom_partition_kwargs: Dict[str, Any] = Field(default_factory=dict, description="Custom kwargs for partition functions")
    
    class Config:
        use_enum_values = True