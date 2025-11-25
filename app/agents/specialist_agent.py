from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent, AgentState
from app.core.logger import setup_logger

logger = setup_logger(__name__)

class SpecialistAgent(BaseAgent):
    def __init__(self, name: str, role: str, model: str = None, temperature: float = 0.7):
        super().__init__(name, role, model, temperature)
        self.specialization = role
        self.expertise_level = 1.0
    
    async def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        self.state = AgentState.EXECUTING
        context = context or {}
        
        try:
            prompt = self._build_prompt(task, context)
            result = await self.think(prompt)
            
            self.state = AgentState.COMPLETED
            return {
                "agent": self.name,
                "role": self.role,
                "task": task,
                "result": result,
                "status": "success"
            }
        except Exception as e:
            self.state = AgentState.FAILED
            self.metrics["tasks_failed"] += 1
            logger.error(f"Agent {self.name} execution failed: {e}")
            return {
                "agent": self.name,
                "role": self.role,
                "task": task,
                "error": str(e),
                "status": "failed"
            }
    
    def _build_prompt(self, task: str, context: Dict[str, Any]) -> str:
        return f"""You are {self.name}, a specialist in {self.role}.

Task: {task}

Context: {context}

Execute this task with your expertise. Provide detailed, actionable results."""

class CoderAgent(SpecialistAgent):
    def __init__(self, model: str = "mistralai/codestral-22b-instruct-v0.1"):
        super().__init__("Coder", "Software Development", model, 0.3)
    
    def _build_prompt(self, task: str, context: Dict[str, Any]) -> str:
        return f"""You are an expert software engineer.

Task: {task}
Context: {context}

Provide clean, efficient, production-ready code with comments."""

class ResearcherAgent(SpecialistAgent):
    def __init__(self, model: str = "meta/llama-3.1-405b-instruct"):
        super().__init__("Researcher", "Research & Analysis", model, 0.7)
    
    def _build_prompt(self, task: str, context: Dict[str, Any]) -> str:
        return f"""You are a research specialist.

Task: {task}
Context: {context}

Provide comprehensive research with sources and insights."""

class AnalystAgent(SpecialistAgent):
    def __init__(self, model: str = "nvidia/nemotron-4-340b-instruct"):
        super().__init__("Analyst", "Data Analysis", model, 0.5)
    
    def _build_prompt(self, task: str, context: Dict[str, Any]) -> str:
        return f"""You are a data analyst.

Task: {task}
Context: {context}

Provide detailed analysis with metrics and recommendations."""

class StrategistAgent(SpecialistAgent):
    def __init__(self, model: str = "meta/llama-3.1-405b-instruct"):
        super().__init__("Strategist", "Strategic Planning", model, 0.8)
    
    def _build_prompt(self, task: str, context: Dict[str, Any]) -> str:
        return f"""You are a strategic planner.

Task: {task}
Context: {context}

Provide strategic recommendations with implementation roadmap."""

class DesignerAgent(SpecialistAgent):
    def __init__(self, model: str = "meta/llama-3.2-90b-vision-instruct"):
        super().__init__("Designer", "Design & UX", model, 0.9)
    
    def _build_prompt(self, task: str, context: Dict[str, Any]) -> str:
        return f"""You are a design specialist.

Task: {task}
Context: {context}

Provide design recommendations with user experience focus."""
