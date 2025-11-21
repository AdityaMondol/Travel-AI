from typing import Any, Dict
from .base_agent import BaseAgent

class ShoppingAgent(BaseAgent):
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        destination = context.get("destination")
        
        prompt = f"""You are a shopping expert. Provide shopping recommendations for {destination}.
        Include: luxury shopping districts, local markets, best souvenirs to buy, and bargaining tips.
        
        Return ONLY valid JSON in this format:
        {{
            "luxury_districts": ["string"],
            "local_markets": [
                {{"name": "string", "specialty": "string", "best_time": "string"}}
            ],
            "souvenirs": [
                {{"item": "string", "approx_price": "string", "where_to_buy": "string"}}
            ],
            "bargaining_tips": ["string"]
        }}"""
        
        result = self.generate_json(prompt)
        return {"shopping": result} if result else {"shopping": {}}
