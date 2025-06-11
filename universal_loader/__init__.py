"""
Universal Data Loader for LLMs using Unstructured
"""

from .loader import UniversalDataLoader
from .config import LoaderConfig

__version__ = "0.1.0"
__all__ = ["UniversalDataLoader", "LoaderConfig"]