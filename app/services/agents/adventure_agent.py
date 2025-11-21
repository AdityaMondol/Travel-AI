from typing import Any, Dict
from .base_agent import BaseAgent

class AdventureAgent(BaseAgent):
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        destination = context.get("destination")
        
        prompt = f"""You are an adventure travel expert. Provide adrenaline-pumping activities for {destination}.
        Include: extreme sports, hiking trails, water sports, and unique adventure experiences.
        
        Return ONLY valid JSON in this format:
        {{
            "extreme_sports": [
                {{"activity": "string", "location": "string", "difficulty": "string", "cost": "string"}}
            ],
            "hiking_trails": [
                {{"name": "string", "difficulty": "string", "duration": "string", "highlights": "string"}}
            ],
            "water_sports": ["string"],
            "unique_experiences": ["string"]
        }}"""
        
        result = self.generate_json(prompt)
        return {"adventure": result} if result else {"adventure": {}}
