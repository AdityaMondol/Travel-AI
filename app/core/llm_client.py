from typing import Optional, Dict, Any
import requests
import time
import json as json_lib
from app.core.config import settings
from app.core.logger import setup_logger

logger = setup_logger(__name__)

class LLMClient:
    def __init__(self, provider: str = None, model: str = None):
        self.provider = provider or settings.LLM_PROVIDER
        self.model = model or self._get_default_model()
        self.api_key = self._get_api_key()
        self.base_url = self._get_base_url()
        self.max_retries = settings.MAX_RETRIES
        self.retry_delay = settings.RETRY_DELAY
    
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
    
    def _retry_with_backoff(self, func, *args, **kwargs) -> Optional[str]:
        """Retry logic with exponential backoff"""
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"Timeout on attempt {attempt + 1}, retrying in {wait_time}s")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Max retries exceeded for timeout")
                    raise
            except requests.exceptions.ConnectionError as e:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"Connection error on attempt {attempt + 1}, retrying in {wait_time}s")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Max retries exceeded for connection error")
                    raise
            except Exception as e:
                if attempt < self.max_retries - 1 and self._is_retryable(e):
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"Error on attempt {attempt + 1}: {e}, retrying in {wait_time}s")
                    time.sleep(wait_time)
                else:
                    raise
        return None
    
    def _is_retryable(self, error: Exception) -> bool:
        """Check if error is retryable"""
        retryable_messages = ["429", "500", "502", "503", "504", "timeout"]
        error_str = str(error).lower()
        return any(msg in error_str for msg in retryable_messages)
    
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2048) -> Optional[str]:
        try:
            if self.provider == "openrouter":
                return self._retry_with_backoff(self._generate_openrouter, prompt, temperature, max_tokens)
            elif self.provider == "google":
                return self._retry_with_backoff(self._generate_google, prompt, temperature, max_tokens)
            elif self.provider == "nvidia":
                return self._retry_with_backoff(self._generate_nvidia, prompt, temperature, max_tokens)
        except Exception as e:
            logger.error(f"Generation error after retries: {e}")
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
        response = requests.post(f"{self.base_url}/chat/completions", json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    
    def _generate_google(self, prompt: str, temperature: float, max_tokens: int) -> Optional[str]:
        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    
    def _generate_nvidia(self, prompt: str, temperature: float, max_tokens: int) -> Optional[str]:
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
        try:
            response = requests.post(f"{self.base_url}/chat/completions", json=payload, headers=headers, timeout=90)
            
            if response.status_code == 401:
                logger.error("Invalid NVIDIA API key")
                raise ValueError("Invalid API key")
            
            response.raise_for_status()
            data = response.json()
            
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"]
                logger.info(f"Generated response: {len(content)} chars")
                return content
            
            logger.error(f"Unexpected response format: {data}")
            raise ValueError("No choices in response")
        except requests.exceptions.Timeout:
            logger.error("NVIDIA API timeout - request took too long")
            raise
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            raise
        except Exception as e:
            logger.error(f"NVIDIA API error: {e}")
            raise
    
    def generate_json(self, prompt: str) -> Optional[Dict[str, Any]]:
        json_prompt = f"{prompt}\n\nRespond with valid JSON only."
        response = self.generate(json_prompt)
        if response:
            try:
                return json_lib.loads(response)
            except json_lib.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                return None
        return None
    
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
            "base_url": self.base_url,
            "max_retries": self.max_retries
        }
