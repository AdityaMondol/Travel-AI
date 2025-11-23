import asyncio
import json
from typing import Dict, Any, AsyncGenerator
from app.core.logger import setup_logger
from app.services.agent_network import AgentNetwork

logger = setup_logger(__name__)

class LangGraphOrchestrator:
    def __init__(self):
        self.network = AgentNetwork()
    
    async def run(self, destination: str, language: str = "en") -> Dict[str, Any]:
        try:
            result = await self.network.run(destination, language)
            return result
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            return {"error": str(e)}
    
    async def run_stream(self, destination: str, language: str = "en") -> AsyncGenerator[str, None]:
        try:
            async for event in self.network.run_stream(destination, language):
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

async def create_travel_plan_langgraph(destination: str, language: str = "en") -> Dict[str, Any]:
    orchestrator = LangGraphOrchestrator()
    return await orchestrator.run(destination, language)
