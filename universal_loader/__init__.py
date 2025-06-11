"""
Universal Data Loader for LLMs using Unstructured
"""

from .loader import UniversalDataLoader
from .config import LoaderConfig, OutputFormat, ChunkingStrategy
from .document import Document, DocumentCollection
from .batch_config import BatchConfig, InputSource, InputType, OutputConfig
from .batch_processor import BatchProcessor

__version__ = "0.1.0"
__all__ = [
    "UniversalDataLoader", 
    "LoaderConfig", 
    "OutputFormat", 
    "ChunkingStrategy",
    "Document", 
    "DocumentCollection",
    "BatchConfig",
    "InputSource", 
    "InputType",
    "OutputConfig",
    "BatchProcessor"
]