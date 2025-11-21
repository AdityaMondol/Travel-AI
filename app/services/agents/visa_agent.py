from typing import Any, Dict
from .base_agent import BaseAgent

class VisaAgent(BaseAgent):
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        destination = context.get("destination")
        origin = context.get("origin", "USA") # Default to USA if not specified
        
        prompt = f"""You are a visa and immigration expert. Provide visa requirements for a traveler from {origin} visiting {destination}.
        Include: visa type needed, application process, fees, validity, and embassy contact info.
        
        Return ONLY valid JSON in this format:
        {{
            "visa_required": true,
            "visa_type": "string",
            "application_process": ["string"],
            "documents_needed": ["string"],
            "fees": "string",
            "validity": "string",
            "embassy_contact": {{
                "address": "string",
                "phone": "string",
                "website": "string"
            }}
        }}"""
        
        result = self.generate_json(prompt)
        return {"visa": result} if result else {"visa": {}}
