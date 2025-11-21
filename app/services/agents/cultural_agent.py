from typing import Any, Dict
from .base_agent import BaseAgent

class CulturalAgent(BaseAgent):
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        destination = context.get("destination")
        
        prompt = f"""You are a cultural expert. Provide a deep dive into the culture of {destination}.
        Include: language, customs, etiquette, local cuisine overview, festivals, do's and don'ts, legal info, visa requirements, illegal activities to avoid, and emergency contacts.
        
        Return ONLY valid JSON in this format: 
        {{
            "culture": "string", 
            "languages": ["string"], 
            "customs": ["string"], 
            "local_cuisine": "string", 
            "festivals": "string", 
            "dos": ["string"], 
            "donts": ["string"], 
            "legal_info": "string", 
            "visa_requirements": "string", 
            "illegal_activities": ["string"], 
            "emergency_contacts": {{
                "police": "string", 
                "ambulance": "string", 
                "embassy": "string"
            }}
        }}"""
        
        result = self.generate_json(prompt)
        return {"culture_and_laws": result} if result else {"culture_and_laws": {}}
