from typing import Optional, Dict, Any
from app.core.config import settings
from app.core.logger import setup_logger
from app.core.llm.factory import LLMFactory

logger = setup_logger(__name__)

class LLMClient:
    def __init__(self, model: str = None):
        self.client = LLMFactory.create_client(model=model)
    
    def generate(self, prompt: str, use_cache: bool = True, temperature: float = 0.7, max_tokens: int = 2048) -> Optional[str]:
        return self.client.generate_text(prompt)
    
    def generate_json(self, prompt: str, use_cache: bool = True) -> Optional[str]:
        return self.client.generate_json(prompt)
    
    def batch_generate(self, prompts: list, use_cache: bool = True) -> list:
        results = []
        for prompt in prompts:
            result = self.generate(prompt, use_cache=use_cache)
            results.append(result)
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "provider": settings.LLM_PROVIDER,
            "model": self.client.model
        }
