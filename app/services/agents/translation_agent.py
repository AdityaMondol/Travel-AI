from typing import Any, Dict
from .base_agent import BaseAgent

class TranslationAgent(BaseAgent):
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        destination = context.get("destination")
        mother_tongue = context.get("mother_tongue", "en")
        
        prompt = f"""You are a linguistic expert. Provide essential translation help for a traveler going to {destination} who speaks {mother_tongue}.
        Include: basic greetings, emergency phrases, dining vocabulary, and pronunciation guide.
        
        Return ONLY valid JSON in this format:
        {{
            "local_language": "string",
            "basic_greetings": [
                {{"phrase": "string", "translation": "string", "pronunciation": "string"}}
            ],
            "emergency_phrases": [
                {{"phrase": "string", "translation": "string", "pronunciation": "string"}}
            ],
            "dining_vocabulary": [
                {{"word": "string", "translation": "string", "pronunciation": "string"}}
            ],
            "cultural_notes": ["string"]
        }}"""
        
        result = self.generate_json(prompt)
        return {"translation": result} if result else {"translation": {}}
