from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class BaseLLMClient(ABC):
    @abstractmethod
    def generate_text(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        pass

    @abstractmethod
    def generate_json(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        pass
