import os
import httpx
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class NIMClient:
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://integrate.api.nvidia.com/v1"):
        self.api_key = api_key or os.getenv("NVIDIA_API_KEY")
        if not self.api_key:
            logger.warning("NVIDIA_API_KEY not found. NIM calls will fail.")
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def chat_completion(self, model: str, messages: List[Dict[str, str]], temperature: float = 0.7) -> Dict[str, Any]:
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "top_p": 1,
            "max_tokens": 1024,
            "stream": False
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=self.headers, timeout=60.0)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"NIM Chat Completion failed: {e}")
                raise

    async def embed(self, model: str, input_text: str | List[str]) -> List[List[float]]:
        url = f"{self.base_url}/embeddings"
        payload = {
            "model": model,
            "input": input_text,
            "encoding_format": "float"
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=self.headers, timeout=60.0)
                response.raise_for_status()
                data = response.json()
                return [item["embedding"] for item in data["data"]]
            except httpx.HTTPError as e:
                logger.error(f"NIM Embedding failed: {e}")
                raise

    async def image_generate(self, prompt: str, model: str = "stabilityai/stable-diffusion-xl-base-1.0") -> str:
        # Note: This is a placeholder for the actual NIM image generation endpoint structure
        # Adjust URL and payload based on specific NIM model API
        url = f"{self.base_url}/images/generations" # Hypothetical endpoint
        payload = {
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024"
        }
        # Implementation would go here
        logger.info(f"Generating image for prompt: {prompt}")
        return "base64_image_data_placeholder"

nim_client = NIMClient()
