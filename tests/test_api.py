"""API tests"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "Leonore AI"

def test_chat_invalid_request():
    """Test chat with invalid request"""
    response = client.post("/api/chat", json={
        "session_id": "",
        "message": ""
    })
    assert response.status_code == 422  # Validation error

def test_chat_valid_request():
    """Test chat with valid request"""
    response = client.post("/api/chat", json={
        "session_id": "test_session",
        "message": "Hello"
    })
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream"

def test_agents_endpoint():
    """Test agents endpoint"""
    response = client.get("/api/agents")
    assert response.status_code == 200
    data = response.json()
    assert "orchestrator" in data
    assert "agent_pool" in data

def test_memory_endpoint():
    """Test memory endpoint"""
    response = client.get("/api/memory")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "count" in data

def test_memory_search():
    """Test memory search"""
    response = client.get("/api/memory?query=test&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert data["count"] <= 5
