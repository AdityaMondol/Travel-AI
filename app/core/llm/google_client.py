import time
import requests
from typing import Optional
from app.core.config import settings
from app.core.logger import setup_logger
from app.core.cache_manager import CacheManager
from .base_client import BaseLLMClient

logger = setup_logger(__name__)

class GoogleClient(BaseLLMClient):
    def __init__(self, model: str = "gemini-pro"):
        self.api_key = settings.GOOGLE_API_KEY
        self.model = model
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        self.cache = CacheManager()

    def generate_text(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        if not self.api_key:
            logger.error("Google API Key not found")
            return None

        cached = self.cache.get(prompt)
        if cached:
            return cached

        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

        for attempt in range(3):
            try:
                response = requests.post(
                    f"{self.base_url}?key={self.api_key}",
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [{"parts": [{"text": full_prompt}]}]
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "candidates" in data and data["candidates"]:
                        content = data["candidates"][0]["content"]["parts"][0]["text"]
                        self.cache.set(prompt, content)
                        return content
                
                logger.warning(f"Google API error: {response.text}")
                time.sleep(2)
            except Exception as e:
                logger.error(f"Google generation failed: {e}")
                time.sleep(2)
        
        return None

    def generate_json(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        json_prompt = f"{prompt}\n\nReturn ONLY valid JSON, no other text."
        return self.generate_text(json_prompt, system_prompt)
