import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_get_languages():
    response = client.get("/api/languages")
    assert response.status_code == 200
    assert "languages" in response.json()
    assert len(response.json()["languages"]) > 0

def test_generate_guide_missing_destination():
    response = client.post("/api/generate", json={})
    assert response.status_code == 422

def test_generate_guide_mock(mocker):
    # Mock the APIServer.generate_travel_guide method
    mocker.patch("app.main.api_server.generate_travel_guide", return_value={
        "status": "success",
        "destination": "Test City",
        "data": {"test": "data"},
        "timestamp": "2025-01-01T00:00:00"
    })
    
    response = client.post("/api/generate", json={"destination": "Test City"})
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["destination"] == "Test City"
