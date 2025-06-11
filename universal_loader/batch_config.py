"""
Batch processing configuration for Universal Data Loader
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, validator
from pathlib import Path
from enum import Enum

from .config import LoaderConfig


class InputType(str, Enum):
    FILE = "file"
    DIRECTORY = "directory"
    URL = "url"


class InputSource(BaseModel):
    """Configuration for a single input source"""
    
    type: InputType = Field(description="Type of input source")
    path: str = Field(description="Path, URL, or directory location")
    recursive: bool = Field(default=True, description="For directories: process recursively")
    include_patterns: Optional[List[str]] = Field(default=None, description="File patterns to include (e.g., ['*.pdf', '*.docx'])")
    exclude_patterns: Optional[List[str]] = Field(default=None, description="File patterns to exclude")
    custom_config: Optional[Dict[str, Any]] = Field(default=None, description="Override config for this source")
    output_prefix: Optional[str] = Field(default=None, description="Prefix for output file naming")
    
    @validator('path')
    def validate_path(cls, v, values):
        """Validate path based on input type"""
        input_type = values.get('type')
        
        if input_type == InputType.FILE:
            # For files, check if it's a valid path format
            if not v or v.startswith(('http://', 'https://')):
                raise ValueError("File input must be a valid file path")
        elif input_type == InputType.URL:
            # For URLs, check if it starts with http/https
            if not v.startswith(('http://', 'https://')):
                raise ValueError("URL input must start with http:// or https://")
        elif input_type == InputType.DIRECTORY:
            # For directories, just check it's not a URL
            if v.startswith(('http://', 'https://')):
                raise ValueError("Directory input cannot be a URL")
        
        return v


class OutputConfig(BaseModel):
    """Configuration for output handling"""
    
    base_path: str = Field(description="Base path for output files")
    merge_all: bool = Field(default=False, description="Merge all sources into single output")
    separate_by_source: bool = Field(default=True, description="Create separate files per source")
    include_source_info: bool = Field(default=True, description="Include source information in metadata")
    filename_template: str = Field(default="{source_name}_{timestamp}", description="Template for output filenames")


class BatchConfig(BaseModel):
    """Configuration for batch processing multiple sources"""
    
    # Processing configuration
    loader_config: LoaderConfig = Field(default_factory=LoaderConfig, description="Default loader configuration")
    
    # Input sources
    sources: List[InputSource] = Field(description="List of input sources to process")
    
    # Output configuration  
    output: OutputConfig = Field(description="Output configuration")
    
    # Processing options
    max_workers: int = Field(default=1, description="Maximum number of parallel workers")
    continue_on_error: bool = Field(default=True, description="Continue processing if one source fails")
    verbose: bool = Field(default=False, description="Verbose output during processing")
    
    # Metadata options
    add_batch_metadata: bool = Field(default=True, description="Add batch processing metadata")
    batch_id: Optional[str] = Field(default=None, description="Custom batch identifier")
    
    @validator('sources')
    def validate_sources(cls, v):
        """Ensure at least one source is provided"""
        if not v:
            raise ValueError("At least one input source must be provided")
        return v
    
    @validator('max_workers')
    def validate_max_workers(cls, v):
        """Ensure reasonable number of workers"""
        if v < 1:
            raise ValueError("max_workers must be at least 1")
        if v > 10:
            raise ValueError("max_workers should not exceed 10 for stability")
        return v


def create_batch_config_from_dict(config_dict: Dict[str, Any]) -> BatchConfig:
    """Create BatchConfig from dictionary (loaded from JSON/YAML)"""
    return BatchConfig(**config_dict)


def create_simple_batch_config(
    sources: List[str], 
    output_dir: str = "output",
    source_types: Optional[List[str]] = None
) -> BatchConfig:
    """
    Create a simple batch configuration from a list of sources
    
    Args:
        sources: List of file paths, directory paths, or URLs
        output_dir: Directory for output files
        source_types: Optional list of source types (auto-detected if None)
    """
    input_sources = []
    
    for i, source in enumerate(sources):
        # Auto-detect source type if not provided
        if source_types and i < len(source_types):
            source_type = InputType(source_types[i])
        else:
            if source.startswith(('http://', 'https://')):
                source_type = InputType.URL
            elif Path(source).is_dir() if Path(source).exists() else source.endswith('/'):
                source_type = InputType.DIRECTORY
            else:
                source_type = InputType.FILE
        
        input_source = InputSource(
            type=source_type,
            path=source,
            output_prefix=f"source_{i+1}"
        )
        input_sources.append(input_source)
    
    output_config = OutputConfig(
        base_path=output_dir,
        separate_by_source=True,
        merge_all=False
    )
    
    return BatchConfig(
        sources=input_sources,
        output=output_config
    )


def create_url_batch_config(
    urls: List[str],
    output_dir: str = "url_outputs"
) -> BatchConfig:
    """Create batch configuration for processing multiple URLs"""
    
    sources = []
    for i, url in enumerate(urls):
        source = InputSource(
            type=InputType.URL,
            path=url,
            output_prefix=f"url_{i+1}"
        )
        sources.append(source)
    
    output_config = OutputConfig(
        base_path=output_dir,
        separate_by_source=True,
        merge_all=False,
        filename_template="{source_name}_webpage"
    )
    
    return BatchConfig(
        sources=sources,
        output=output_config,
        loader_config=LoaderConfig(
            remove_headers_footers=True
        )
    )


def create_directory_batch_config(
    directories: List[str],
    output_dir: str = "directory_outputs",
    recursive: bool = True
) -> BatchConfig:
    """Create batch configuration for processing multiple directories"""
    
    sources = []
    for i, directory in enumerate(directories):
        dir_name = Path(directory).name or f"dir_{i+1}"
        source = InputSource(
            type=InputType.DIRECTORY,
            path=directory,
            recursive=recursive,
            output_prefix=dir_name
        )
        sources.append(source)
    
    output_config = OutputConfig(
        base_path=output_dir,
        separate_by_source=True,
        merge_all=False,
        filename_template="{source_name}_collection"
    )
    
    return BatchConfig(
        sources=sources,
        output=output_config
    )