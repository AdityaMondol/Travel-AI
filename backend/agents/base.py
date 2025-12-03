from abc import ABC, abstractmethod
from typing import Dict, Any, List
from backend.utils.nim_client import nim_client
from backend.services.db import db_service
import logging

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    def __init__(self, agent_id: str, job_id: str):
        self.agent_id = agent_id
        self.job_id = job_id
        self.model = "meta/llama3-70b-instruct" # Default model

    @abstractmethod
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution method for the agent.
        """
        pass

    async def log_activity(self, action: str, details: Dict[str, Any]):
        """
        Logs agent activity to the audit log.
        """
        db_service.log_audit(self.job_id, f"{self.agent_id}:{action}", details)
        logger.info(f"[{self.job_id}] {self.agent_id}: {action}")

    async def call_llm(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """
        Helper to call NIM LLM.
        """
        response = await nim_client.chat_completion(self.model, messages, temperature)
        return response["choices"][0]["message"]["content"]
