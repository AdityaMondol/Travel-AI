"""Base agent with LangGraph integration"""
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime
import uuid
from app.core.logger import setup_logger
from app.core.audit import get_audit_log, AuditEventType


logger = setup_logger(__name__)


class AgentState(str, Enum):
    """Agent lifecycle states"""
    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING = "executing"
    WAITING = "waiting"
    COMPLETE = "complete"
    ERROR = "error"


class BaseAgent:
    """Base agent with state management and audit trail"""
    
    def __init__(self, agent_id: str, agent_type: str, config: Dict[str, Any] = None):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.config = config or {}
        self.state = AgentState.IDLE
        self.created_at = datetime.utcnow()
        self.last_action = None
        self.action_history: List[Dict[str, Any]] = []
        self.memory: Dict[str, Any] = {}
        self.audit_log = get_audit_log()
        self.cost_used = 0.0
    
    async def initialize(self):
        """Initialize agent"""
        await self.audit_log.log_event(
            AuditEventType.AGENT_SPAWN,
            "system",
            self.agent_id,
            "initialize",
            {"agent_type": self.agent_type, "config": self.config}
        )
        logger.info(f"Agent initialized: {self.agent_id} ({self.agent_type})")
    
    async def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task"""
        self.state = AgentState.THINKING
        
        try:
            await self.audit_log.log_event(
                AuditEventType.AGENT_ACTION,
                self.agent_id,
                "task",
                "execute",
                {"task": task, "context_keys": list(context.keys())}
            )
            
            result = await self._execute_internal(task, context)
            
            self.state = AgentState.COMPLETE
            self.last_action = {
                "task": task,
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.action_history.append(self.last_action)
            
            return result
        
        except Exception as e:
            self.state = AgentState.ERROR
            logger.error(f"Agent execution error: {e}")
            
            await self.audit_log.log_event(
                AuditEventType.AGENT_ACTION,
                self.agent_id,
                "task",
                "execute",
                {"task": task, "error": str(e)},
                result="error"
            )
            
            raise
    
    async def _execute_internal(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Internal execution logic (override in subclasses)"""
        return {"status": "not_implemented"}
    
    def get_state(self) -> Dict[str, Any]:
        """Get agent state"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "state": self.state.value,
            "created_at": self.created_at.isoformat(),
            "last_action": self.last_action,
            "action_count": len(self.action_history),
            "cost_used": self.cost_used,
        }
    
    def store_memory(self, key: str, value: Any):
        """Store in agent memory"""
        self.memory[key] = value
    
    def retrieve_memory(self, key: str) -> Optional[Any]:
        """Retrieve from agent memory"""
        return self.memory.get(key)
    
    async def cleanup(self):
        """Cleanup agent resources"""
        self.state = AgentState.IDLE
        logger.info(f"Agent cleaned up: {self.agent_id}")


class SpecialistAgent(BaseAgent):
    """Specialist agent for specific domains"""
    
    SPECIALISTS = {
        "researcher": "Deep research and information gathering",
        "coder": "Code generation and debugging",
        "analyst": "Data analysis and visualization",
        "strategist": "Planning and strategy",
        "designer": "UI/UX design",
    }
    
    def __init__(self, specialist_type: str, config: Dict[str, Any] = None):
        if specialist_type not in self.SPECIALISTS:
            raise ValueError(f"Unknown specialist type: {specialist_type}")
        
        agent_id = f"{specialist_type}_{uuid.uuid4().hex[:8]}"
        super().__init__(agent_id, f"specialist_{specialist_type}", config)
        self.specialist_type = specialist_type
    
    async def _execute_internal(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute specialist task"""
        from app.core.llm_client import get_llm_client
        
        llm = get_llm_client()
        
        # Build specialist prompt
        prompt = f"""You are a {self.specialist_type} specialist.
Task: {task}
Context: {context}

Provide a detailed response."""
        
        response = await llm.generate(prompt)
        
        return {
            "specialist": self.specialist_type,
            "task": task,
            "response": response,
            "timestamp": datetime.utcnow().isoformat()
        }
