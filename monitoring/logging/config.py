"""
Logging Configuration
Structured logging setup for the microservice
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Any
from config.settings import settings


def setup_logging() -> logging.Logger:
    """Setup structured logging for the application"""
    
    # Create logger
    logger = logging.getLogger("universal_data_loader")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler for production
    if settings.ENVIRONMENT == "production":
        log_file = Path("/app/logs/app.log")
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "universal_data_loader") -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)


# Initialize logging
setup_logging()