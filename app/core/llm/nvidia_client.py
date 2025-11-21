import time
import requests
from typing import Optional
from app.core.config import settings
from app.core.logger import setup_logger
from app.core.cache_manager import CacheManager
from .base_client import BaseLLMClient

logger = setup_logger(__name__)

class NVIDIAClient(BaseLLMClient):
    def __init__(self, model: str = "nvidia/llama-3.1-nemotron-70b-instruct"):
        self.api_key = settings.NVIDIA_API_KEY
        self.model = model
        self.base_url = "https://integrate.api.nvidia.com/v1/chat/completions"
        self.cache = CacheManager()

    def generate_text(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        if not self.api_key:
            logger.error("NVIDIA API Key not found")
            return None

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
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": 0.5,
                        "top_p": 1,
                        "max_tokens": 1024
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    content = response.json()["choices"][0]["message"]["content"]
                    self.cache.set(prompt, content)
                    return content
                
                logger.warning(f"NVIDIA API error: {response.text}")
                time.sleep(2)
            except Exception as e:
                logger.error(f"NVIDIA generation failed: {e}")
                time.sleep(2)
        
        return None

    def generate_json(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        json_prompt = f"{prompt}\n\nReturn ONLY valid JSON, no other text."
        return self.generate_text(json_prompt, system_prompt)
