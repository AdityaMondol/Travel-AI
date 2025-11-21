from typing import Any, Dict
from .base_agent import BaseAgent

class HistoryAgent(BaseAgent):
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        destination = context.get("destination")
        
        prompt = f"""You are a historian. Provide a fascinating historical overview of {destination}.
        Include: key historical eras, founding story, significant historical figures, and 3 hidden historical gems not usually known to tourists.
        
        Return ONLY valid JSON in this format:
        {{
            "founding_story": "string",
            "key_eras": [
                {{"era": "string", "description": "string"}}
            ],
            "historical_figures": ["string"],
            "hidden_gems": [
                {{"name": "string", "description": "string", "location": "string"}}
            ]
        }}"""
        
        result = self.generate_json(prompt)
        return {"history": result} if result else {"history": {}}
