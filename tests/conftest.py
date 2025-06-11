"""
Pytest Configuration
Shared fixtures and test configuration
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """FastAPI test client fixture"""
    return TestClient(app)


@pytest.fixture
def sample_config():
    """Sample configuration for testing"""
    return {
        "output_format": "documents",
        "include_metadata": True,
        "max_chunk_size": 1000,
        "chunk_overlap": 100
    }


@pytest.fixture
def sample_batch_config():
    """Sample batch configuration for testing"""
    return {
        "sources": [
            {"type": "url", "path": "https://httpbin.org/html"}
        ],
        "loader_config": {
            "output_format": "documents",
            "include_metadata": True
        },
        "max_workers": 2,
        "continue_on_error": True
    }