from typing import Any, Dict, List
from .base_agent import BaseAgent
from app.models.models import Place

class PlacesAgent(BaseAgent):
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        destination = context.get("destination")
        if not destination:
            return {}

        prompt = f"""You are an expert travel guide. Provide comprehensive information about 8 popular places to visit in {destination}. 
        For each place, include: name, rating (0-5), detailed description, facilities available, image_url (use a placeholder if unknown), best time to visit, entry fee, and estimated duration.
        
        Return ONLY valid JSON in this format: 
        {{
            "places": [
                {{
                    "name": "string", 
                    "rating": number, 
                    "description": "string", 
                    "facilities": ["string"], 
                    "image_url": "string", 
                    "best_time": "string", 
                    "entry_fee": "string", 
                    "duration": "string"
                }}
            ]
        }}"""
        
        result = self.generate_json(prompt)
        if result and "places" in result:
            # Validate with Pydantic (optional but good practice)
            # places = [Place(**p) for p in result["places"]]
            return {"places": result}
        return {"places": {"places": []}}
