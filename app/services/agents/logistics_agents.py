from typing import Any, Dict
from .base_agent import BaseAgent

class BudgetAgent(BaseAgent):
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        destination = context.get("destination")
        
        prompt = f"""You are a financial advisor specializing in travel. Provide detailed budget information for {destination}.
        Include: daily costs for different traveler types, cost breakdown, money tips, local currency, exchange rate info, best payment methods, and free activities.
        
        Return ONLY valid JSON in this format: 
        {{
            "daily_costs": {{
                "budget_traveler": "string", 
                "mid_range": "string", 
                "luxury": "string"
            }}, 
            "cost_breakdown": {{
                "accommodation": "string", 
                "food": "string", 
                "transport": "string", 
                "activities": "string", 
                "misc": "string"
            }}, 
            "money_tips": ["string"], 
            "local_currency": "string", 
            "exchange_rate_info": "string", 
            "best_payment_methods": ["string"], 
            "free_activities": ["string"]
        }}"""
        
        result = self.generate_json(prompt)
        return {"budget": result} if result else {"budget": {}}

class TransportAgent(BaseAgent):
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        destination = context.get("destination")
        
        prompt = f"""You are a logistics expert. Provide comprehensive travel and navigation information for {destination}.
        Include: ways to get there, local transport options, navigation tips, safety tips, best travel times, airport information, and transportation costs.
        
        Return ONLY valid JSON in this format: 
        {{
            "getting_there": ["string"], 
            "local_transport": {{
                "taxis": "string", 
                "public_transport": "string", 
                "rentals": "string"
            }}, 
            "navigation_tips": ["string"], 
            "safety_tips": ["string"], 
            "best_travel_times": "string", 
            "airport_info": "string", 
            "transportation_costs": "string"
        }}"""
        
        result = self.generate_json(prompt)
        return {"transport": result} if result else {"transport": {}}

class SafetyAgent(BaseAgent):
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        destination = context.get("destination")
        
        prompt = f"""You are a safety expert. Provide comprehensive safety and health information for {destination}.
        Include: safety level, areas to avoid, required vaccinations, health tips, travel insurance recommendations, hospital quality, pharmacy availability, water safety, emergency numbers, and health risks.
        
        Return ONLY valid JSON in this format: 
        {{
            "safety_level": "string", 
            "areas_to_avoid": ["string"], 
            "vaccinations": ["string"], 
            "health_tips": ["string"], 
            "travel_insurance": "string", 
            "hospitals": "string", 
            "pharmacies": "string", 
            "water_safety": "string", 
            "emergency_numbers": ["string"], 
            "health_risks": ["string"]
        }}"""
        
        result = self.generate_json(prompt)
        return {"safety_health": result} if result else {"safety_health": {}}
