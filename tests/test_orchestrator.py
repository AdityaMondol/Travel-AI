import pytest
from unittest.mock import MagicMock
from app.services.orchestrator import Orchestrator
from app.core.llm.base_client import BaseLLMClient

class MockLLMClient(BaseLLMClient):
    def generate(self, prompt: str, **kwargs) -> str:
        return '{"test": "response"}'
    
    async def generate_async(self, prompt: str, **kwargs) -> str:
        return '{"test": "response"}'
        
    def generate_text(self, prompt: str, system_prompt: str = None) -> str:
        return '{"test": "response"}'
        
    def generate_json(self, prompt: str, system_prompt: str = None) -> str:
        return '{"test": "response"}'

@pytest.fixture
def orchestrator():
    llm_client = MockLLMClient()
    return Orchestrator(llm_client)

@pytest.mark.asyncio
async def test_orchestrator_run_stream(orchestrator):
    destination = "Paris"
    mother_tongue = "en"
    
    # Mock the agents to avoid actual LLM calls
    for agent in orchestrator.agents.values():
        agent.execute = MagicMock(return_value={"mock": "data"})
    
    # We need to mock the run_stream method partially or just test the generator
    # Since run_stream calls agent.execute, and we mocked it, it should be fast.
    
    chunks = []
    async for chunk in orchestrator.run_stream(destination, mother_tongue):
        chunks.append(chunk)
    
    assert len(chunks) > 0
    # Check for start and complete events
    assert 'type' in chunks[0] and 'start' in chunks[0]
    assert 'type' in chunks[-1] and 'complete' in chunks[-1]

def test_orchestrator_initialization(orchestrator):
    assert len(orchestrator.agents) > 0
    assert "history" in orchestrator.agents
    assert "weather" in orchestrator.agents
