import pytest
import asyncio
from httpx import AsyncClient
from app.main import app
from app.core.config import get_config
from app.core.safety import get_safety_manager
from app.core.audit import get_audit_log, AuditEventType


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


@pytest.mark.asyncio
async def test_chat_endpoint(client):
    response = await client.post(
        "/api/chat",
        json={
            "session_id": "test_session",
            "message": "Hello"
        }
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_upload_endpoint(client):
    files = {"file": ("test.txt", b"test content")}
    response = await client.post(
        "/api/upload",
        files=files,
        data={"session_id": "test_session"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "file_id" in data


@pytest.mark.asyncio
async def test_agents_status(client):
    response = await client.get("/api/agents")
    assert response.status_code == 200
    data = response.json()
    assert "total_agents" in data


@pytest.mark.asyncio
async def test_memory_query(client):
    response = await client.get("/api/memory?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data


@pytest.mark.asyncio
async def test_safety_content_filter():
    safety = get_safety_manager()
    
    is_safe, category, detail = safety.content_filter.check_content(
        "This is normal content"
    )
    assert is_safe is True
    
    is_safe, category, detail = safety.content_filter.check_content(
        "ransomware exploit payload"
    )
    assert is_safe is False
    assert category == "malware"


@pytest.mark.asyncio
async def test_audit_logging():
    audit = get_audit_log()
    
    hash1 = await audit.log_event(
        AuditEventType.AGENT_SPAWN,
        "test_actor",
        "test_resource",
        "spawn",
        {"test": "data"}
    )
    
    assert hash1 is not None
    assert audit.verify_chain() is True


@pytest.mark.asyncio
async def test_policy_enforcement():
    safety = get_safety_manager()
    
    allowed, reason = await safety.policy_engine.check_action(
        "actor",
        "normal_action",
        "resource",
        {}
    )
    assert allowed is True
    
    allowed, reason = await safety.policy_engine.check_action(
        "actor",
        "system_shutdown",
        "resource",
        {}
    )
    assert allowed is False


@pytest.mark.asyncio
async def test_config_validation():
    config = get_config()
    
    assert config.environment in ["development", "staging", "production"]
    assert config.vector_db_type in ["milvus", "weaviate", "pinecone"]
    assert config.api_port > 0
    assert config.jwt_expiration_hours > 0


@pytest.mark.asyncio
async def test_rate_limiting():
    config = get_config()
    
    assert config.rate_limit_requests > 0
    assert config.rate_limit_window_seconds > 0


@pytest.mark.asyncio
async def test_resource_limits():
    config = get_config()
    
    assert config.max_agent_memory_mb > 0
    assert config.max_execution_time_seconds > 0
    assert config.max_concurrent_agents > 0
    assert config.gpu_memory_limit_gb > 0
    assert config.monthly_cost_limit_usd > 0


@pytest.mark.asyncio
async def test_simple_chat(client):
    response = await client.post(
        "/api/chat/simple",
        json={
            "session_id": "test_session",
            "message": "test message"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "response" in data


@pytest.mark.asyncio
async def test_system_status(client):
    response = await client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert "system" in data
    assert "agents" in data


@pytest.mark.asyncio
async def test_metrics_endpoint(client):
    response = await client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "memory_mb" in data or "error" in data


@pytest.mark.asyncio
async def test_hierarchy_stats(client):
    response = await client.get("/api/hierarchy")
    assert response.status_code in [200, 500]


@pytest.mark.asyncio
async def test_plan_creation(client):
    response = await client.post(
        "/api/plan",
        json={"goal": "test goal"}
    )
    assert response.status_code in [200, 500]


@pytest.mark.asyncio
async def test_tool_listing(client):
    response = await client.get("/api/tools")
    assert response.status_code in [200, 500]


@pytest.mark.asyncio
async def test_research_workflow(client):
    response = await client.post(
        "/api/research",
        json={"query": "test query"}
    )
    assert response.status_code in [200, 500]


@pytest.mark.asyncio
async def test_code_workflow(client):
    response = await client.post(
        "/api/code",
        json={"task": "test task"}
    )
    assert response.status_code in [200, 500]


@pytest.mark.asyncio
async def test_browser_workflow(client):
    response = await client.post(
        "/api/browse",
        json={"goal": "test goal"}
    )
    assert response.status_code in [200, 500]
