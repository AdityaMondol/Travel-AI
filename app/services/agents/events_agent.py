from typing import Any, Dict
from .base_agent import BaseAgent

class EventsAgent(BaseAgent):
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        destination = context.get("destination")
        
        prompt = f"""You are an events specialist. Provide information on local events in {destination}.
        Include: major annual festivals, local markets, music concerts, and cultural exhibitions.
        
        Return ONLY valid JSON in this format:
        {{
            "festivals": [
                {{"name": "string", "date": "string", "description": "string"}}
            ],
            "concerts": [
                {{"name": "string", "venue": "string", "date": "string"}}
            ],
            "exhibitions": [
                {{"name": "string", "location": "string", "dates": "string"}}
            ],
            "local_markets": [
                {{"name": "string", "schedule": "string"}}
            ]
        }}"""
        
        result = self.generate_json(prompt)
        return {"events": result} if result else {"events": {}}
