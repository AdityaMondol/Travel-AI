from typing import Dict, Any, List
import json
from backend.agents.base import BaseAgent

class PlannerAgent(BaseAgent):
    def __init__(self, job_id: str):
        super().__init__("planner", job_id)
        self.model = "meta/llama3-70b-instruct" # Good for reasoning

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        objective = input_data.get("objective")
        self.log_activity("planning_started", {"objective": objective})

        prompt = f"""
        You are an expert project planner for an autonomous agent system.
        Objective: {objective}
        
        Available Agents:
        - researcher: Web scraping, RAG, information gathering.
        - coder: Writing code, testing, debugging.
        - ppt: Creating slide decks.
        - browser: Automating browser tasks.
        - verifier: Fact-checking and auditing.
        
        Create a detailed, step-by-step plan to achieve the objective.
        Return ONLY a JSON object with the following structure:
        {{
            "plan": [
                {{
                    "step_id": 1,
                    "agent": "agent_name",
                    "instruction": "Detailed instruction for the agent",
                    "dependencies": [] 
                }}
            ]
        }}
        """
        
        response = await self.call_llm([{"role": "user", "content": prompt}], temperature=0.2)
        
        try:
            # Basic cleanup for JSON parsing if model adds markdown blocks
            clean_response = response.replace("```json", "").replace("```", "").strip()
            plan = json.loads(clean_response)
            self.log_activity("planning_complete", {"plan": plan})
            return plan
        except json.JSONDecodeError:
            self.log_activity("planning_failed", {"error": "Invalid JSON response", "raw": response})
            raise ValueError("Failed to generate a valid plan.")

