from typing import Optional
from app.core.config import settings
from .base_client import BaseLLMClient
from .openrouter_client import OpenRouterClient
from .google_client import GoogleClient
from .nvidia_client import NVIDIAClient

class LLMFactory:
    @staticmethod
    def create_client(provider: str = None, model: str = None) -> BaseLLMClient:
        provider = provider or settings.LLM_PROVIDER
        
        if provider == "google":
            return GoogleClient(model=model or "gemini-pro")
        elif provider == "nvidia":
            return NVIDIAClient(model=model or "nvidia/llama-3.1-nemotron-70b-instruct")
        else:
            return OpenRouterClient(model=model)
