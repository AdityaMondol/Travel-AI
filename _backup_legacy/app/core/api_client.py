import asyncio
import json
from typing import Any, Dict, Optional, Callable
import aiohttp
from app.core.logger import setup_logger

logger = setup_logger(__name__)

class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            url = f"{self.base_url}{endpoint}"
            async with self.session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"API error: {response.status}")
                    return {"error": f"HTTP {response.status}"}
        except asyncio.TimeoutError:
            logger.error("API request timeout")
            return {"error": "Request timeout"}
        except Exception as e:
            logger.error(f"API error: {e}")
            return {"error": str(e)}
    
    async def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            url = f"{self.base_url}{endpoint}"
            async with self.session.post(
                url,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status in [200, 201]:
                    return await response.json()
                else:
                    logger.error(f"API error: {response.status}")
                    return {"error": f"HTTP {response.status}"}
        except asyncio.TimeoutError:
            logger.error("API request timeout")
            return {"error": "Request timeout"}
        except Exception as e:
            logger.error(f"API error: {e}")
            return {"error": str(e)}
    
    async def stream(self, endpoint: str, data: Dict[str, Any], callback: Callable):
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            url = f"{self.base_url}{endpoint}"
            async with self.session.post(
                url,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=300)
            ) as response:
                if response.status == 200:
                    async for line in response.content:
                        if line:
                            try:
                                event = json.loads(line.decode('utf-8').replace('data: ', ''))
                                await callback(event)
                            except json.JSONDecodeError:
                                pass
                else:
                    logger.error(f"Stream error: {response.status}")
        except Exception as e:
            logger.error(f"Stream error: {e}")
