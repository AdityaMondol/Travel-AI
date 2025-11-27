"""NVIDIA NIM client with retry logic and cost tracking"""
import httpx
import asyncio
from typing import Optional, Dict, Any, AsyncGenerator
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import get_config
from app.core.logger import setup_logger


logger = setup_logger(__name__)


class NIMClient:
    """NVIDIA NIM API client"""
    
    def __init__(self):
        self.config = get_config()
        self.base_url = self.config.nvidia_api_base
        self.api_key = self.config.nvidia_api_key
        self.model = self.config.nim_model
        self.vision_model = self.config.nim_vision_model
        self.total_tokens = 0
        self.total_cost = 0.0
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> str:
        """Generate text using NIM"""
        model = model or self.model
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=self._get_headers()
            )
            response.raise_for_status()
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            # Track tokens and cost
            tokens = data.get("usage", {}).get("total_tokens", 0)
            self.total_tokens += tokens
            self._update_cost(tokens)
            
            return content
    
    async def stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream text generation"""
        model = model or self.model
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
            **kwargs
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=self._get_headers()
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        
                        try:
                            import json
                            data = json.loads(data_str)
                            delta = data.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except:
                            pass
    
    async def embed(self, text: str, model: str = "nvidia/nv-embed-qa-e5-v5") -> list[float]:
        """Generate embeddings"""
        payload = {
            "model": model,
            "input": text,
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/embeddings",
                json=payload,
                headers=self._get_headers()
            )
            response.raise_for_status()
            
            data = response.json()
            return data["data"][0]["embedding"]
    
    def _update_cost(self, tokens: int):
        """Update cost tracking (approximate)"""
        # Rough estimate: $0.001 per 1K tokens for Llama 3.1 405B
        cost = (tokens / 1000) * 0.001
        self.total_cost += cost
        
        if self.total_cost > self.config.monthly_cost_limit_usd:
            logger.warning(f"Monthly cost limit approaching: ${self.total_cost:.2f}")
    
    def get_usage(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return {
            "total_tokens": self.total_tokens,
            "total_cost": f"${self.total_cost:.4f}",
            "cost_limit": f"${self.config.monthly_cost_limit_usd:.2f}",
        }


class LLMClient:
    """Unified LLM client (can swap providers)"""
    
    def __init__(self, provider: str = "nvidia"):
        self.provider = provider
        
        if provider == "nvidia":
            self.client = NIMClient()
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text"""
        return await self.client.generate(prompt, **kwargs)
    
    async def stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """Stream text"""
        async for chunk in self.client.stream(prompt, **kwargs):
            yield chunk
    
    async def embed(self, text: str) -> list[float]:
        """Generate embeddings"""
        return await self.client.embed(text)
    
    def get_usage(self) -> Dict[str, Any]:
        """Get usage stats"""
        return self.client.get_usage()


def get_llm_client() -> LLMClient:
    """Get LLM client"""
    return LLMClient(provider="nvidia")
