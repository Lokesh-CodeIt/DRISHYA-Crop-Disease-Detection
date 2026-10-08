"""
Unit tests for LeafLens FastAPI endpoints and health status.
"""

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["project"] == "LeafLens"
    assert data["status"] == "online"


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "turmeric" in data["supported_crops"]
    assert "citrus" in data["supported_crops"]
