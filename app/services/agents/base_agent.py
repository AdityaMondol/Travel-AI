from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from langchain.tools import Tool
from app.core.logger import setup_logger

logger = setup_logger(__name__)

class BaseAgent(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.tools = []
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    def add_tool(self, tool: Tool):
        self.tools.append(tool)
    
    def get_tools(self):
        return self.tools
