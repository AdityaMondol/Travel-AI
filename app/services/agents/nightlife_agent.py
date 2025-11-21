from typing import Any, Dict
from .base_agent import BaseAgent

class NightlifeAgent(BaseAgent):
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        destination = context.get("destination")
        
        prompt = f"""You are a nightlife expert. Provide nightlife recommendations for {destination}.
        Include: top clubs, best bars, live music venues, and safe evening areas.
        
        Return ONLY valid JSON in this format:
        {{
            "top_clubs": [
                {{"name": "string", "vibe": "string", "entry_fee": "string"}}
            ],
            "bars": [
                {{"name": "string", "specialty": "string"}}
            ],
            "live_music": ["string"],
            "safe_areas": ["string"]
        }}"""
        
        result = self.generate_json(prompt)
        return {"nightlife": result} if result else {"nightlife": {}}
