import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.agents.base_agent import BaseAgent, AgentState
from app.agents.specialist_agent import (
    CoderAgent, ResearcherAgent, AnalystAgent, 
    StrategistAgent, DesignerAgent, SpecialistAgent
)
from app.agents.planner import AutonomousPlanner
from app.agents.hierarchy_manager import HierarchyManager
from app.tools.dynamic_tool_creator import DynamicToolCreator
from app.core.overdrive_mode import overdrive_system
from app.core.logger import setup_logger

logger = setup_logger(__name__)

class OrchestratorAgent(BaseAgent):
    def __init__(self, model: str = "meta/llama-3.1-405b-instruct"):
        super().__init__("Orchestrator", "Multi-Agent Coordination", model, 0.7)
        self.agent_pool: Dict[str, BaseAgent] = {}
        self.task_queue: List[Dict[str, Any]] = []
        self.results: List[Dict[str, Any]] = []
        self.planner = AutonomousPlanner(self)
        self.hierarchy = HierarchyManager()
        self.tool_creator = DynamicToolCreator()
        self._initialize_specialists()
    
    def _initialize_specialists(self):
        specialists = [
            CoderAgent(),
            ResearcherAgent(),
            AnalystAgent(),
            StrategistAgent(),
            DesignerAgent()
        ]
        for agent in specialists:
            self.agent_pool[agent.role] = agent
            logger.info(f"Initialized specialist: {agent.name}")
    
    async def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        self.state = AgentState.EXECUTING
        context = context or {}
        
        try:
            plan = await self._create_plan(task, context)
            subtasks = plan.get("subtasks", [])
            
            results = await self._execute_parallel(subtasks, context)
            
            synthesis = await self._synthesize_results(task, results)
            
            self.state = AgentState.COMPLETED
            return {
                "task": task,
                "plan": plan,
                "results": results,
                "synthesis": synthesis,
                "status": "success",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.state = AgentState.FAILED
            logger.error(f"Orchestrator execution failed: {e}")
            return {
                "task": task,
                "error": str(e),
                "status": "failed"
            }
    
    async def _create_plan(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        available_agents = list(self.agent_pool.keys())
        
        planning_prompt = f"""Create an execution plan for this task:

Task: {task}
Context: {context}
Available specialists: {available_agents}

Provide a JSON plan with:
1. subtasks: list of subtasks with assigned specialist
2. dependencies: task dependencies
3. parallel_groups: tasks that can run in parallel

Format:
{{
    "subtasks": [
        {{"id": 1, "description": "...", "specialist": "...", "priority": 1}}
    ],
    "dependencies": {{"2": [1]}},
    "parallel_groups": [[1, 3], [2, 4]]
}}"""
        
        plan_text = await self.think(planning_prompt)
        
        import json
        try:
            plan = json.loads(plan_text)
        except:
            plan = {
                "subtasks": [
                    {"id": 1, "description": task, "specialist": "Research & Analysis", "priority": 1}
                ],
                "dependencies": {},
                "parallel_groups": [[1]]
            }
        
        return plan
    
    async def _execute_parallel(self, subtasks: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        tasks = []
        for subtask in subtasks:
            specialist_role = subtask.get("specialist", "Research & Analysis")
            agent = self.agent_pool.get(specialist_role)
            
            if not agent:
                agent = SpecialistAgent(
                    f"Dynamic_{specialist_role}", 
                    specialist_role,
                    "meta/llama-3.1-70b-instruct"
                )
                self.agent_pool[specialist_role] = agent
            
            task_coro = agent.execute(subtask.get("description", ""), context)
            tasks.append(task_coro)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "subtask_id": i,
                    "error": str(result),
                    "status": "failed"
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _synthesize_results(self, task: str, results: List[Dict[str, Any]]) -> str:
        synthesis_prompt = f"""Synthesize these results into a coherent response:

Original task: {task}

Results from specialists:
{results}

Provide a comprehensive, unified response."""
        
        try:
            response = await self.think(synthesis_prompt)
            if response:
                return response
            return f"Task completed: {task}"
        except Exception as e:
            logger.error(f"Synthesis error: {e}")
            return f"Task completed: {task}"
    
    async def spawn_dynamic_agent(self, role: str, task: str, model: str = None) -> Dict[str, Any]:
        agent = SpecialistAgent(
            f"Dynamic_{role}_{len(self.agent_pool)}", 
            role,
            model or "meta/llama-3.1-70b-instruct"
        )
        self.agent_pool[role] = agent
        
        result = await agent.execute(task)
        return result
    
    def get_system_status(self) -> Dict[str, Any]:
        return {
            "orchestrator": self.get_status(),
            "agent_pool": {
                role: agent.get_status() 
                for role, agent in self.agent_pool.items()
            },
            "total_agents": len(self.agent_pool),
            "task_queue_size": len(self.task_queue),
            "results_count": len(self.results)
        }
