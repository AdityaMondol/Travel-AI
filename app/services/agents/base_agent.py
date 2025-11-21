from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from app.core.llm_client import LLMClient
from app.core.logger import setup_logger

logger = setup_logger(__name__)

class BaseAgent(ABC):
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.name = self.__class__.__name__
        self.memory: List[Dict[str, Any]] = []

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's task based on the provided context.
        Returns a dictionary of results to be merged into the shared context.
        """
        pass

    def generate_json(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Helper method to generate JSON using the LLM client.
        """
        try:
            # Add memory context if available
            if self.memory:
                memory_context = "\nPrevious interactions:\n" + "\n".join([str(m) for m in self.memory])
                prompt = f"{memory_context}\n\n{prompt}"

            response = self.llm_client.generate_json(prompt)
            if response:
                import json
                # Handle potential markdown code blocks
                cleaned_response = response.replace("```json", "").replace("```", "").strip()
                result = json.loads(cleaned_response)
                
                # Update memory
                self.memory.append({"prompt": prompt[:100] + "...", "response": result})
                return result
        except Exception as e:
            logger.error(f"Agent {self.name} failed to generate JSON: {e}")
        return None

    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Return a list of tools available to this agent.
        """
        return []
