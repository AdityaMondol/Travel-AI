from typing import Dict, List, Any, Optional
from app.core.logger import setup_logger

logger = setup_logger(__name__)

class RecommendationEngine:
    """Generate personalized recommendations based on user preferences"""
    
    @staticmethod
    def get_recommendations(
        destination: str,
        travel_style: str = "balanced",
        budget_level: str = "moderate",
        interests: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate personalized recommendations"""
        
        interests = interests or ["culture", "food", "nature"]
        
        recommendations = {
            "travel_style": travel_style,
            "budget_level": budget_level,
            "interests": interests,
            "suggested_activities": RecommendationEngine._get_activities(travel_style, interests),
            "budget_breakdown": RecommendationEngine._get_budget_breakdown(budget_level),
            "best_time_to_visit": "Spring or Fall",
            "packing_tips": RecommendationEngine._get_packing_tips(destination),
            "local_customs": RecommendationEngine._get_local_customs(destination)
        }
        
        return recommendations
    
    @staticmethod
    def _get_activities(travel_style: str, interests: List[str]) -> List[str]:
        """Get activity recommendations based on style"""
        activities_map = {
            "adventure": [
                "Hiking and trekking",
                "Water sports",
                "Rock climbing",
                "Paragliding",
                "Mountain biking"
            ],
            "cultural": [
                "Museum visits",
                "Historical site tours",
                "Local market exploration",
                "Cultural performances",
                "Art gallery visits"
            ],
            "relaxation": [
                "Spa treatments",
                "Beach lounging",
                "Yoga sessions",
                "Meditation retreats",
                "Wellness centers"
            ],
            "balanced": [
                "Sightseeing tours",
                "Local restaurant dining",
                "Shopping",
                "Photography walks",
                "Day trips"
            ]
        }
        
        return activities_map.get(travel_style, activities_map["balanced"])
    
    @staticmethod
    def _get_budget_breakdown(budget_level: str) -> Dict[str, str]:
        """Get budget breakdown recommendations"""
        breakdowns = {
            "budget": {
                "accommodation": "$20-40/night",
                "food": "$5-15/day",
                "activities": "$5-20/day",
                "transport": "$10-30/day"
            },
            "moderate": {
                "accommodation": "$50-100/night",
                "food": "$20-40/day",
                "activities": "$30-60/day",
                "transport": "$20-50/day"
            },
            "luxury": {
                "accommodation": "$150+/night",
                "food": "$50+/day",
                "activities": "$100+/day",
                "transport": "$50+/day"
            }
        }
        
        return breakdowns.get(budget_level, breakdowns["moderate"])
    
    @staticmethod
    def _get_packing_tips(destination: str) -> List[str]:
        """Get packing tips for destination"""
        return [
            "Check weather forecast before packing",
            "Pack comfortable walking shoes",
            "Bring universal power adapter",
            "Include travel insurance documents",
            "Pack medications and first aid kit",
            "Bring copies of important documents",
            "Pack light, breathable clothing",
            "Include sun protection items"
        ]
    
    @staticmethod
    def _get_local_customs(destination: str) -> List[str]:
        """Get local customs and etiquette tips"""
        return [
            "Learn basic local greetings",
            "Respect local dress codes",
            "Ask permission before photographing people",
            "Be respectful in religious sites",
            "Tip appropriately (check local customs)",
            "Don't point with one finger",
            "Remove shoes when entering homes",
            "Avoid discussing sensitive political topics"
        ]
