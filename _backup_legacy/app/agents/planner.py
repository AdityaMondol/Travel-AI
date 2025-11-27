import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.core.logger import setup_logger

logger = setup_logger(__name__)

class AutonomousPlanner:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.plans: Dict[str, Dict[str, Any]] = {}
    
    async def create_multi_step_plan(self, goal: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        planning_prompt = f"""
Create a detailed multi-step execution plan for this goal:

Goal: {goal}
Context: {context}

Provide a comprehensive plan with:
1. Goal decomposition into atomic subtasks
2. Dependencies between tasks
3. Required resources and agents
4. Risk assessment for each step
5. Fallback strategies
6. Success criteria
7. Estimated timeline

Format as JSON with this structure:
{{
    "goal": "...",
    "steps": [
        {{
            "id": 1,
            "description": "...",
            "agent_type": "...",
            "dependencies": [],
            "resources": [],
            "risk_level": "low|medium|high",
            "fallback": "...",
            "success_criteria": "..."
        }}
    ],
    "parallel_groups": [[1,2], [3,4,5]],
    "total_estimated_time": "...",
    "critical_path": [1,3,5]
}}"""

        plan_text = await self.orchestrator.think(planning_prompt)
        
        import json
        try:
            plan = json.loads(plan_text)
        except:
            plan = {
                "goal": goal,
                "steps": [{"id": 1, "description": goal, "agent_type": "generalist"}],
                "parallel_groups": [[1]]
            }
        
        plan_id = f"plan_{datetime.now().timestamp()}"
        plan["id"] = plan_id
        plan["created_at"] = datetime.now().isoformat()
        plan["status"] = "pending"
        
        self.plans[plan_id] = plan
        return plan
    
    async def execute_plan(self, plan_id: str) -> Dict[str, Any]:
        if plan_id not in self.plans:
            return {"error": "Plan not found"}
        
        plan = self.plans[plan_id]
        plan["status"] = "executing"
        plan["started_at"] = datetime.now().isoformat()
        
        results = []
        
        for group in plan.get("parallel_groups", []):
            group_tasks = []
            
            for step_id in group:
                step = next((s for s in plan["steps"] if s["id"] == step_id), None)
                if not step:
                    continue
                
                task = self._execute_step(step, plan)
                group_tasks.append(task)
            
            group_results = await asyncio.gather(*group_tasks, return_exceptions=True)
            results.extend(group_results)
        
        plan["status"] = "completed"
        plan["completed_at"] = datetime.now().isoformat()
        plan["results"] = results
        
        return plan
    
    async def _execute_step(self, step: Dict[str, Any], plan: Dict[str, Any]) -> Dict[str, Any]:
        agent_type = step.get("agent_type", "generalist")
        
        agent = self.orchestrator.agent_pool.get(agent_type)
        if not agent:
            agent = await self.orchestrator.spawn_dynamic_agent(
                agent_type,
                step["description"]
            )
        
        try:
            result = await agent.execute(step["description"], {"plan": plan, "step": step})
            
            if not self._check_success_criteria(result, step.get("success_criteria")):
                if step.get("fallback"):
                    logger.warning(f"Step {step['id']} failed criteria, executing fallback")
                    result = await agent.execute(step["fallback"], {"plan": plan, "step": step})
            
            return {
                "step_id": step["id"],
                "status": "success",
                "result": result
            }
        except Exception as e:
            logger.error(f"Step {step['id']} failed: {e}")
            return {
                "step_id": step["id"],
                "status": "failed",
                "error": str(e)
            }
    
    def _check_success_criteria(self, result: Any, criteria: Optional[str]) -> bool:
        if not criteria:
            return True
        
        return "success" in str(result).lower()
    
    async def adapt_plan(self, plan_id: str, feedback: str) -> Dict[str, Any]:
        if plan_id not in self.plans:
            return {"error": "Plan not found"}
        
        plan = self.plans[plan_id]
        
        adaptation_prompt = f"""
Adapt this plan based on feedback:

Original plan: {plan}
Feedback: {feedback}

Provide an updated plan that addresses the feedback while maintaining the core goal.
Format as JSON with the same structure."""

        adapted_text = await self.orchestrator.think(adaptation_prompt)
        
        import json
        try:
            adapted_plan = json.loads(adapted_text)
            adapted_plan["id"] = plan_id
            adapted_plan["adapted_at"] = datetime.now().isoformat()
            adapted_plan["adaptation_reason"] = feedback
            self.plans[plan_id] = adapted_plan
            return adapted_plan
        except:
            return {"error": "Failed to adapt plan"}
