"""Multi-agent orchestrator with LangGraph"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
from app.agents.base_agent import BaseAgent, SpecialistAgent, AgentState
from app.core.logger import setup_logger
from app.core.safety import get_safety_manager
from app.core.audit import get_audit_log, AuditEventType


logger = setup_logger(__name__)


class OrchestratorAgent(BaseAgent):
    """Orchestrator for managing multiple agents"""
    
    def __init__(self):
        super().__init__("orchestrator_main", "orchestrator")
        self.agent_pool: Dict[str, BaseAgent] = {}
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        self.safety_manager = get_safety_manager()
        self.audit_log = get_audit_log()
    
    async def initialize(self):
        """Initialize orchestrator"""
        await super().initialize()
        
        # Spawn initial specialist agents
        for specialist_type in SpecialistAgent.SPECIALISTS.keys():
            agent = SpecialistAgent(specialist_type)
            await agent.initialize()
            self.agent_pool[agent.agent_id] = agent
        
        logger.info(f"Orchestrator initialized with {len(self.agent_pool)} agents")
    
    async def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task with multi-agent coordination"""
        
        # Safety validation
        is_safe, reason = await self.safety_manager.validate_request(
            actor="orchestrator",
            action="execute_task",
            resource="task",
            content=task,
            context=context
        )
        
        if not is_safe:
            logger.warning(f"Task blocked by safety: {reason}")
            return {"status": "blocked", "reason": reason}
        
        # Route to appropriate agent
        agent = self._select_agent(task)
        
        if not agent:
            logger.error("No suitable agent found")
            return {"status": "error", "reason": "No suitable agent"}
        
        # Execute with agent
        result = await agent.execute(task, context)
        
        # Track task
        task_id = str(uuid.uuid4())
        self.active_tasks[task_id] = {
            "task": task,
            "agent_id": agent.agent_id,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return {
            "status": "success",
            "task_id": task_id,
            "agent_id": agent.agent_id,
            "result": result
        }
    
    def _select_agent(self, task: str) -> Optional[BaseAgent]:
        """Select best agent for task"""
        task_lower = task.lower()
        
        # Simple routing logic
        if any(word in task_lower for word in ["research", "search", "find", "investigate"]):
            return self._get_agent_by_type("researcher")
        elif any(word in task_lower for word in ["code", "write", "generate", "debug"]):
            return self._get_agent_by_type("coder")
        elif any(word in task_lower for word in ["analyze", "data", "chart", "graph"]):
            return self._get_agent_by_type("analyst")
        elif any(word in task_lower for word in ["plan", "strategy", "design"]):
            return self._get_agent_by_type("strategist")
        elif any(word in task_lower for word in ["ui", "ux", "design", "layout"]):
            return self._get_agent_by_type("designer")
        
        # Default to first available agent
        for agent in self.agent_pool.values():
            if agent.state == AgentState.IDLE:
                return agent
        
        return None
    
    def _get_agent_by_type(self, specialist_type: str) -> Optional[BaseAgent]:
        """Get agent by specialist type"""
        for agent in self.agent_pool.values():
            if isinstance(agent, SpecialistAgent) and agent.specialist_type == specialist_type:
                if agent.state == AgentState.IDLE:
                    return agent
        
        return None
    
    async def spawn_agent(self, agent_type: str, config: Dict[str, Any] = None) -> str:
        """Spawn new agent"""
        if agent_type in SpecialistAgent.SPECIALISTS:
            agent = SpecialistAgent(agent_type, config)
        else:
            agent = BaseAgent(f"agent_{uuid.uuid4().hex[:8]}", agent_type, config)
        
        await agent.initialize()
        self.agent_pool[agent.agent_id] = agent
        
        await self.audit_log.log_event(
            AuditEventType.AGENT_SPAWN,
            "orchestrator",
            agent.agent_id,
            "spawn",
            {"agent_type": agent_type, "config": config}
        )
        
        logger.info(f"Agent spawned: {agent.agent_id}")
        return agent.agent_id
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status"""
        active_agents = sum(1 for a in self.agent_pool.values() if a.state != AgentState.IDLE)
        
        return {
            "total_agents": len(self.agent_pool),
            "active_agents": active_agents,
            "idle_agents": len(self.agent_pool) - active_agents,
            "active_tasks": len(self.active_tasks),
            "agents": [
                {
                    "id": agent.agent_id,
                    "type": agent.agent_type,
                    "state": agent.state.value,
                    "cost": agent.cost_used
                }
                for agent in self.agent_pool.values()
            ]
        }
    
    async def cleanup(self):
        """Cleanup all agents"""
        for agent in self.agent_pool.values():
            await agent.cleanup()
        
        self.agent_pool.clear()
        logger.info("Orchestrator cleaned up")
