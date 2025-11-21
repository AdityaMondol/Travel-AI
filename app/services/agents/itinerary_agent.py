from typing import Any, Dict
from .base_agent import BaseAgent

class ItineraryAgent(BaseAgent):
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        destination = context.get("destination")
        places_data = context.get("places", {}).get("places", [])
        
        places_context = ""
        if places_data:
            places_names = [p.get("name") for p in places_data]
            places_context = f"Consider including these top rated places: {', '.join(places_names)}."

        prompt = f"""You are an elite itinerary planning expert. Create detailed sample itineraries for {destination} for different trip durations.
        {places_context}
        
        For each day, include: day number, activities (be specific), meals (suggestions), and accommodation area. Also provide general travel tips.
        
        Return ONLY valid JSON in this format: 
        {{
            "three_days": [
                {{"day": number, "activities": ["string"], "meals": ["string"], "accommodation": "string"}}
            ], 
            "five_days": [
                {{"day": number, "activities": ["string"], "meals": ["string"], "accommodation": "string"}}
            ], 
            "seven_days": [
                {{"day": number, "activities": ["string"], "meals": ["string"], "accommodation": "string"}}
            ], 
            "tips": ["string"]
        }}"""
        
        result = self.generate_json(prompt)
        return {"itinerary": result} if result else {"itinerary": {}}
