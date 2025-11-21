from typing import Any, Dict
from .base_agent import BaseAgent

class PhotographyAgent(BaseAgent):
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        destination = context.get("destination")
        
        prompt = f"""You are a professional photographer. Provide the best photography spots in {destination}.
        Include: iconic shots, hidden angles, best time of day for each spot, and gear recommendations.
        
        Return ONLY valid JSON in this format:
        {{
            "photo_spots": [
                {{"name": "string", "description": "string", "best_time": "string", "tips": "string"}}
            ],
            "instagrammable_places": ["string"],
            "gear_recommendations": ["string"]
        }}"""
        
        result = self.generate_json(prompt)
        return {"photography": result} if result else {"photography": {}}
