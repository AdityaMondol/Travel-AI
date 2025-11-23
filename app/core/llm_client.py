from typing import Optional, Dict, Any
import requests
from app.core.config import settings
from app.core.logger import setup_logger

logger = setup_logger(__name__)

class LLMClient:
    def __init__(self, provider: str = None, model: str = None):
        self.provider = provider or settings.LLM_PROVIDER
        self.model = model or self._get_default_model()
        self.api_key = self._get_api_key()
        self.base_url = self._get_base_url()
    
    def _get_default_model(self) -> str:
        if self.provider == "openrouter":
            return settings.OPENROUTER_MODEL
        elif self.provider == "google":
            return settings.GOOGLE_MODEL
        elif self.provider == "nvidia":
            return settings.NVIDIA_MODEL
        return settings.OPENROUTER_MODEL
    
    def _get_api_key(self) -> str:
        if self.provider == "openrouter":
            return settings.OPENROUTER_API_KEY
        elif self.provider == "google":
            return settings.GOOGLE_API_KEY
        elif self.provider == "nvidia":
            return settings.NVIDIA_API_KEY
        raise ValueError(f"Unknown provider: {self.provider}")
    
    def _get_base_url(self) -> str:
        if self.provider == "openrouter":
            return "https://openrouter.ai/api/v1"
        elif self.provider == "google":
            return "https://generativelanguage.googleapis.com/v1beta/models"
        elif self.provider == "nvidia":
            return settings.NVIDIA_BASE_URL
        return "https://openrouter.ai/api/v1"
    
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2048) -> Optional[str]:
        try:
            if self.provider == "openrouter":
                return self._generate_openrouter(prompt, temperature, max_tokens)
            elif self.provider == "google":
                return self._generate_google(prompt, temperature, max_tokens)
            elif self.provider == "nvidia":
                return self._generate_nvidia(prompt, temperature, max_tokens)
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return None
    
    def _generate_openrouter(self, prompt: str, temperature: float, max_tokens: int) -> Optional[str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        response = requests.post(f"{self.base_url}/chat/completions", json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return None
    
    def _generate_google(self, prompt: str, temperature: float, max_tokens: int) -> Optional[str]:
        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        return None
    
    def _generate_nvidia(self, prompt: str, temperature: float, max_tokens: int) -> Optional[str]:
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            response = requests.post(f"{self.base_url}/chat/completions", json=payload, headers=headers, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"]
            else:
                logger.error(f"NVIDIA API error: {response.status_code} - {response.text}")
            return None
        except requests.exceptions.Timeout:
            logger.error("NVIDIA API timeout")
            return None
        except Exception as e:
            logger.error(f"NVIDIA API error: {e}")
            return None
    
    def generate_json(self, prompt: str) -> Optional[str]:
        json_prompt = f"{prompt}\n\nRespond with valid JSON only."
        return self.generate(json_prompt)
    
    def batch_generate(self, prompts: list) -> list:
        results = []
        for prompt in prompts:
            result = self.generate(prompt)
            results.append(result)
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.model,
            "base_url": self.base_url
        }
