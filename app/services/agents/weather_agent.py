from typing import Any, Dict
from .base_agent import BaseAgent

class WeatherAgent(BaseAgent):
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        destination = context.get("destination")
        if not destination:
            return {}

        prompt = f"""You are a meteorologist specializing in travel. Provide detailed weather and climate information for {destination}.
        Include: current season, temperature range, best time to visit, rainy season months, humidity levels, packing suggestions, weather alerts, climate type, and travel tips.
        
        Return ONLY valid JSON in this format: 
        {{
            "current_season": "string", 
            "temperature_range": "string", 
            "best_time": "string", 
            "rainy_season": "string", 
            "humidity": "string", 
            "packing_suggestions": ["string"], 
            "weather_alerts": "string", 
            "climate_type": "string", 
            "travel_tips": ["string"]
        }}"""
        
        result = self.generate_json(prompt)
        return {"weather": result} if result else {"weather": {}}
