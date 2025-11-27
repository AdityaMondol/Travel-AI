import json
import hashlib
import time
from pathlib import Path
from typing import Any, Optional
from app.core.config import Config
from app.core.logger import setup_logger

logger = setup_logger(__name__)

class CacheManager:
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = Path(cache_dir)
        self.enabled = Config.CACHE_ENABLED
        self.memory_cache = {}
    
    def _get_cache_key(self, key: str) -> str:
        return hashlib.md5(key.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        if not self.enabled:
            return None
        
        cache_key = self._get_cache_key(key)
        if cache_key in self.memory_cache:
            cached_data = self.memory_cache[cache_key]
            if time.time() - cached_data['timestamp'] < Config.CACHE_TTL:
                return cached_data['value']
            else:
                del self.memory_cache[cache_key]
        
        return None
    
    def set(self, key: str, value: Any) -> bool:
        if not self.enabled:
            return False
        
        try:
            cache_key = self._get_cache_key(key)
            self.memory_cache[cache_key] = {
                'timestamp': time.time(),
                'value': value
            }
            return True
        except Exception:
            return False
    
    def clear(self) -> bool:
        self.memory_cache.clear()
        return True
