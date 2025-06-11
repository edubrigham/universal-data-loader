"""
Application Settings
Environment-based configuration management
"""

import os
from pathlib import Path
from typing import List


class Settings:
    """Application settings with environment variable support"""
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Storage Configuration
    UPLOAD_DIR: Path = Path(os.getenv("UPLOAD_DIR", "/tmp/uploads"))
    OUTPUT_DIR: Path = Path(os.getenv("OUTPUT_DIR", "/tmp/outputs"))
    
    # Processing Configuration
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "100")) * 1024 * 1024  # MB to bytes
    MAX_WORKERS: int = int(os.getenv("MAX_WORKERS", "3"))
    JOB_TIMEOUT: int = int(os.getenv("JOB_TIMEOUT", "300"))  # seconds
    
    # Security Configuration
    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else ["*"]
    API_KEY: str = os.getenv("API_KEY", "")
    RATE_LIMIT: str = os.getenv("RATE_LIMIT", "100/minute")
    
    # Monitoring Configuration
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # OCR Configuration
    OCR_LANGUAGES: List[str] = os.getenv("OCR_LANGUAGES", "eng").split(",")
    
    @classmethod
    def ensure_directories(cls):
        """Ensure required directories exist"""
        cls.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
settings.ensure_directories()