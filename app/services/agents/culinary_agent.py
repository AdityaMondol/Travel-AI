from typing import Any, Dict
from .base_agent import BaseAgent

class CulinaryAgent(BaseAgent):
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        destination = context.get("destination")
        
        prompt = f"""You are a world-class culinary expert. Provide a comprehensive food guide for {destination}.
        Include: must-try dishes, best restaurants (budget, mid-range, fine dining), street food recommendations, dining etiquette, vegetarian options, food safety tips, and local beverages.
        
        Return ONLY valid JSON in this format: 
        {{
            "must_try_dishes": ["string"], 
            "restaurants": {{
                "budget": ["string"], 
                "mid_range": ["string"], 
                "fine_dining": ["string"]
            }}, 
            "street_food": {{
                "popular_items": ["string"], 
                "where_to_find": "string"
            }}, 
            "dining_etiquette": ["string"], 
            "vegetarian_options": "string", 
            "food_safety_tips": ["string"], 
            "local_beverages": ["string"]
        }}"""
        
        result = self.generate_json(prompt)
        return {"food": result} if result else {"food": {}}
