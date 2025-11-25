import asyncio
from typing import Dict, Any, List
from datetime import datetime
from app.core.logger import setup_logger

logger = setup_logger(__name__)

class ReflectionEngine:
    def __init__(self, agent):
        self.agent = agent
        self.reflection_history: List[Dict[str, Any]] = []
        self.performance_metrics = {
            "success_rate": 0.0,
            "avg_quality": 0.0,
            "efficiency": 0.0
        }
    
    async def reflect_on_action(self, action: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        reflection_prompt = f"""
Critically analyze this action and result:

Action: {action}
Result: {result}

Provide:
1. What worked well
2. What failed or could improve
3. Root cause analysis
4. Specific improvements for next time
5. Self-assessment score (0-10)

Be brutally honest and self-critical."""

        reflection = await self.agent.think(reflection_prompt)
        
        reflection_data = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "result": result,
            "reflection": reflection,
            "agent_id": self.agent.id
        }
        
        self.reflection_history.append(reflection_data)
        self._update_metrics(reflection_data)
        
        return reflection_data
    
    async def self_improve(self) -> Dict[str, Any]:
        if len(self.reflection_history) < 3:
            return {"status": "insufficient_data"}
        
        recent = self.reflection_history[-10:]
        
        improvement_prompt = f"""
Analyze your recent performance and identify concrete improvements:

Recent reflections: {recent}
Current metrics: {self.performance_metrics}

Provide:
1. Top 3 recurring mistakes
2. Specific behavioral changes needed
3. New strategies to adopt
4. Skills to develop
5. Action plan for improvement

Be specific and actionable."""

        improvement_plan = await self.agent.think(improvement_prompt)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "improvement_plan": improvement_plan,
            "metrics": self.performance_metrics
        }
    
    def _update_metrics(self, reflection: Dict[str, Any]):
        total = len(self.reflection_history)
        if total > 0:
            successes = sum(1 for r in self.reflection_history if "success" in str(r.get("result", {})).lower())
            self.performance_metrics["success_rate"] = successes / total

class CriticAgent:
    def __init__(self, model: str = "meta/llama-3.1-405b-instruct"):
        from app.core.llm_client import LLMClient
        self.llm = LLMClient(provider="nvidia", model=model)
    
    async def critique(self, output: str, criteria: List[str]) -> Dict[str, Any]:
        critique_prompt = f"""
Critically evaluate this output against these criteria:

Output: {output}

Criteria:
{chr(10).join(f'- {c}' for c in criteria)}

Provide:
1. Score for each criterion (0-10)
2. Specific weaknesses
3. Concrete improvements
4. Overall assessment

Be harsh and thorough."""

        critique = await asyncio.to_thread(self.llm.generate, critique_prompt, 0.3)
        
        return {
            "critique": critique,
            "timestamp": datetime.now().isoformat()
        }
