"""
Utility functions for the Universal Data Loader
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Union
from .config import LoaderConfig, OutputFormat, ChunkingStrategy


def load_config_from_file(config_path: Union[str, Path]) -> LoaderConfig:
    """
    Load configuration from a JSON file
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        LoaderConfig instance
    """
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
        
    return LoaderConfig(**config_data)


def save_config_to_file(config: LoaderConfig, config_path: Union[str, Path]) -> None:
    """
    Save configuration to a JSON file
    
    Args:
        config: LoaderConfig instance to save
        config_path: Path to save the configuration
    """
    config_path = Path(config_path)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config.dict(), f, indent=2, ensure_ascii=False)


def create_default_config() -> LoaderConfig:
    """Create a default configuration for common use cases"""
    return LoaderConfig(
        output_format=OutputFormat.JSON,
        include_metadata=True,
        chunking_strategy=ChunkingStrategy.BY_TITLE,
        max_chunk_size=1000,
        chunk_overlap=100,
        ocr_languages=["eng"],
        extract_images=False,
        min_text_length=10,
        remove_headers_footers=True
    )


def create_config_for_rag() -> LoaderConfig:
    """Create a configuration optimized for RAG applications"""
    return LoaderConfig(
        output_format=OutputFormat.JSON,
        include_metadata=True,
        chunking_strategy=ChunkingStrategy.BY_TITLE,
        max_chunk_size=800,  # Smaller chunks for better retrieval
        chunk_overlap=150,   # More overlap for context preservation
        ocr_languages=["eng"],
        extract_images=False,
        min_text_length=50,  # Filter out very short content
        remove_headers_footers=True
    )


def create_config_for_training() -> LoaderConfig:
    """Create a configuration optimized for model training"""
    return LoaderConfig(
        output_format=OutputFormat.TEXT,
        include_metadata=False,  # Clean text for training
        chunking_strategy=ChunkingStrategy.BASIC,
        max_chunk_size=2000,     # Larger chunks for training
        chunk_overlap=50,        # Minimal overlap
        ocr_languages=["eng"],
        extract_images=False,
        min_text_length=100,     # Filter short content
        remove_headers_footers=True
    )


def get_file_stats(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Get basic statistics about a file
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with file statistics
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
        
    stat = file_path.stat()
    
    return {
        'file_name': file_path.name,
        'file_size': stat.st_size,
        'file_extension': file_path.suffix,
        'last_modified': stat.st_mtime,
        'absolute_path': str(file_path.absolute())
    }


def validate_file_type(file_path: Union[str, Path], 
                      supported_extensions: set) -> bool:
    """
    Validate if a file type is supported
    
    Args:
        file_path: Path to the file
        supported_extensions: Set of supported file extensions
        
    Returns:
        True if file type is supported
    """
    file_path = Path(file_path)
    return file_path.suffix.lower() in supported_extensions


def merge_elements(elements_list: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Merge multiple lists of elements into a single list
    
    Args:
        elements_list: List of element lists to merge
        
    Returns:
        Single merged list of elements
    """
    merged = []
    for elements in elements_list:
        merged.extend(elements)
    return merged


def filter_elements_by_type(elements: List[Dict[str, Any]], 
                           element_types: List[str]) -> List[Dict[str, Any]]:
    """
    Filter elements by their type/category
    
    Args:
        elements: List of elements to filter
        element_types: List of element types to keep
        
    Returns:
        Filtered list of elements
    """
    filtered = []
    for element in elements:
        if isinstance(element, dict):
            element_type = element.get('type', element.get('category', ''))
            if element_type in element_types:
                filtered.append(element)
        else:
            # Handle non-dict elements
            element_type = getattr(element, 'category', '')
            if element_type in element_types:
                filtered.append(element)
    return filtered


def extract_text_only(elements: List[Dict[str, Any]]) -> List[str]:
    """
    Extract only the text content from elements
    
    Args:
        elements: List of elements
        
    Returns:
        List of text strings
    """
    texts = []
    for element in elements:
        if isinstance(element, dict):
            text = element.get('text', '')
        else:
            text = str(element)
        
        if text.strip():
            texts.append(text.strip())
            
    return texts


def count_elements_by_type(elements: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Count elements by their type/category
    
    Args:
        elements: List of elements to count
        
    Returns:
        Dictionary with counts by element type
    """
    counts = {}
    for element in elements:
        if isinstance(element, dict):
            element_type = element.get('type', element.get('category', 'Unknown'))
        else:
            element_type = getattr(element, 'category', 'Unknown')
            
        counts[element_type] = counts.get(element_type, 0) + 1
        
    return counts