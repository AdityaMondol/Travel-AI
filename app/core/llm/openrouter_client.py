import time
import requests
from typing import Optional
from app.core.config import settings
from app.core.logger import setup_logger
from app.core.cache_manager import CacheManager
from .base_client import BaseLLMClient

logger = setup_logger(__name__)

class OpenRouterClient(BaseLLMClient):
    def __init__(self, model: str = None):
        self.api_key = settings.OPENROUTER_API_KEY
        self.model = model or settings.OPENROUTER_MODEL
        self.base_url = "https://openrouter.ai/api/v1"
        self.cache = CacheManager()

    def generate_text(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        cached = self.cache.get(prompt)
        if cached:
            return cached

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        for attempt in range(3):
            try:
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://github.com",
                        "X-Title": "AI Agent Army"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": 0.7
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    content = response.json()["choices"][0]["message"]["content"]
                    self.cache.set(prompt, content)
                    return content
                
                time.sleep(2)
            except Exception as e:
                logger.error(f"OpenRouter generation failed: {e}")
                time.sleep(2)
        
        return None

    def generate_json(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        json_prompt = f"{prompt}\n\nReturn ONLY valid JSON, no other text."
        return self.generate_text(json_prompt, system_prompt)
