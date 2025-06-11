"""
Integration Tests for Health API
"""

import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert data["service"] == "Universal Data Loader API"
    assert data["version"] == "1.0.0"
    assert data["status"] == "running"
    assert "endpoints" in data


def test_health_check(client: TestClient):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "uptime" in data
    assert "active_jobs" in data
    assert isinstance(data["active_jobs"], int)