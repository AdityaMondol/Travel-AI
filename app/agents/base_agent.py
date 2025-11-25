import asyncio
from typing import Dict, Any, Optional, List, Callable
from abc import ABC, abstractmethod
from datetime import datetime
import uuid
from app.core.logger import setup_logger
from app.core.llm_client import LLMClient

logger = setup_logger(__name__)

class AgentState:
    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING = "executing"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"

class BaseAgent(ABC):
    def __init__(self, name: str, role: str, model: str = None, temperature: float = 0.7):
        self.id = str(uuid.uuid4())
        self.name = name
        self.role = role
        self.model = model
        self.temperature = temperature
        self.state = AgentState.IDLE
        self.memory: List[Dict[str, Any]] = []
        self.children: List['BaseAgent'] = []
        self.parent: Optional['BaseAgent'] = None
        self.tools: Dict[str, Callable] = {}
        self.llm = LLMClient(provider="nvidia", model=model)
        self.created_at = datetime.now()
        self.metrics = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_tokens": 0,
            "avg_response_time": 0.0
        }
    
    @abstractmethod
    async def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        pass
    
    async def think(self, prompt: str) -> str:
        self.state = AgentState.THINKING
        start = datetime.now()
        try:
            from app.core.overdrive_mode import overdrive_system
            modifier = overdrive_system.get_system_prompt_modifier(self.id)
            full_prompt = f"{modifier}\n\n{prompt}" if modifier else prompt
            
            response = await asyncio.to_thread(
                self.llm.generate, 
                full_prompt, 
                self.temperature
            )
            
            if not response:
                logger.warning(f"Agent {self.name} received empty response")
                response = f"Processed: {prompt[:100]}"
            
            elapsed = (datetime.now() - start).total_seconds()
            self._update_metrics(elapsed)
            self.memory.append({
                "timestamp": datetime.now().isoformat(),
                "type": "thought",
                "prompt": prompt[:200],
                "response": response[:500] if response else "",
                "elapsed": elapsed,
                "overdrive": overdrive_system.is_unrestricted(self.id)
            })
            self.state = AgentState.COMPLETED
            return response
        except Exception as e:
            logger.error(f"Agent {self.name} think error: {e}")
            self.state = AgentState.FAILED
            return f"Error processing request: {str(e)[:100]}"
    
    async def spawn_child(self, name: str, role: str, model: str = None) -> 'BaseAgent':
        from app.agents.specialist_agent import SpecialistAgent
        child = SpecialistAgent(name, role, model or self.model)
        child.parent = self
        self.children.append(child)
        logger.info(f"Agent {self.name} spawned child {name}")
        return child
    
    def register_tool(self, name: str, func: Callable):
        self.tools[name] = func
        logger.info(f"Agent {self.name} registered tool: {name}")
    
    async def use_tool(self, tool_name: str, **kwargs) -> Any:
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
        self.state = AgentState.EXECUTING
        try:
            result = await asyncio.to_thread(self.tools[tool_name], **kwargs)
            self.memory.append({
                "timestamp": datetime.now().isoformat(),
                "type": "tool_use",
                "tool": tool_name,
                "args": kwargs,
                "result": result
            })
            return result
        except Exception as e:
            logger.error(f"Tool {tool_name} error: {e}")
            raise
    
    async def reflect(self) -> Dict[str, Any]:
        recent_memory = self.memory[-10:] if len(self.memory) > 10 else self.memory
        reflection_prompt = f"""
Reflect on your recent actions and performance:
Role: {self.role}
Recent memory: {recent_memory}
Metrics: {self.metrics}

Provide:
1. What went well
2. What could improve
3. Next actions
"""
        reflection = await self.think(reflection_prompt)
        return {
            "timestamp": datetime.now().isoformat(),
            "reflection": reflection,
            "metrics": self.metrics
        }
    
    def _update_metrics(self, elapsed: float):
        self.metrics["tasks_completed"] += 1
        current_avg = self.metrics["avg_response_time"]
        total = self.metrics["tasks_completed"]
        self.metrics["avg_response_time"] = (current_avg * (total - 1) + elapsed) / total
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "state": self.state,
            "model": self.model,
            "children_count": len(self.children),
            "memory_size": len(self.memory),
            "metrics": self.metrics,
            "uptime": (datetime.now() - self.created_at).total_seconds()
        }
