from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from app.core.logger import setup_logger

logger = setup_logger(__name__)

class ItineraryBuilder:
    """Build and customize travel itineraries"""
    
    @staticmethod
    def create_itinerary(
        destination: str,
        duration_days: int = 3,
        travel_style: str = "balanced",
        interests: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a customized itinerary"""
        
        interests = interests or ["culture", "food", "nature"]
        start_date = datetime.now()
        
        itinerary = {
            "destination": destination,
            "duration_days": duration_days,
            "travel_style": travel_style,
            "interests": interests,
            "start_date": start_date.isoformat(),
            "end_date": (start_date + timedelta(days=duration_days)).isoformat(),
            "days": []
        }
        
        for day_num in range(1, duration_days + 1):
            day_itinerary = ItineraryBuilder._create_day_itinerary(
                day_num, travel_style, interests
            )
            itinerary["days"].append(day_itinerary)
        
        return itinerary
    
    @staticmethod
    def _create_day_itinerary(
        day_num: int,
        travel_style: str,
        interests: List[str]
    ) -> Dict[str, Any]:
        """Create itinerary for a single day"""
        
        activities_by_style = {
            "adventure": [
                "Morning: Hiking or outdoor activity",
                "Lunch: Local restaurant",
                "Afternoon: Water sports or extreme activity",
                "Evening: Sunset viewing"
            ],
            "cultural": [
                "Morning: Museum or historical site",
                "Lunch: Traditional cuisine",
                "Afternoon: Cultural performance or local market",
                "Evening: Local restaurant"
            ],
            "relaxation": [
                "Morning: Yoga or meditation",
                "Lunch: Spa treatment",
                "Afternoon: Beach or nature relaxation",
                "Evening: Wellness dinner"
            ],
            "balanced": [
                "Morning: Sightseeing",
                "Lunch: Local restaurant",
                "Afternoon: Shopping or exploration",
                "Evening: Cultural activity"
            ]
        }
        
        activities = activities_by_style.get(travel_style, activities_by_style["balanced"])
        
        return {
            "day": day_num,
            "date": (datetime.now() + timedelta(days=day_num-1)).isoformat(),
            "activities": activities,
            "meals": {
                "breakfast": "Hotel or local cafe",
                "lunch": "Local restaurant",
                "dinner": "Recommended restaurant"
            },
            "accommodation": "Hotel or Airbnb",
            "estimated_cost": "$100-200"
        }
    
    @staticmethod
    def add_activity(
        itinerary: Dict[str, Any],
        day_num: int,
        activity: str,
        time: str = "afternoon"
    ) -> bool:
        """Add activity to specific day"""
        try:
            if day_num < 1 or day_num > len(itinerary["days"]):
                return False
            
            day = itinerary["days"][day_num - 1]
            day["activities"].append(f"{time.capitalize()}: {activity}")
            logger.info(f"Added activity to day {day_num}: {activity}")
            return True
        except Exception as e:
            logger.error(f"Error adding activity: {e}")
            return False
    
    @staticmethod
    def remove_activity(
        itinerary: Dict[str, Any],
        day_num: int,
        activity_index: int
    ) -> bool:
        """Remove activity from specific day"""
        try:
            if day_num < 1 or day_num > len(itinerary["days"]):
                return False
            
            day = itinerary["days"][day_num - 1]
            if activity_index < 0 or activity_index >= len(day["activities"]):
                return False
            
            removed = day["activities"].pop(activity_index)
            logger.info(f"Removed activity from day {day_num}: {removed}")
            return True
        except Exception as e:
            logger.error(f"Error removing activity: {e}")
            return False
    
    @staticmethod
    def get_day_summary(day_itinerary: Dict[str, Any]) -> str:
        """Get summary of day's activities"""
        summary = f"Day {day_itinerary['day']}: "
        summary += " → ".join(day_itinerary["activities"][:3])
        if len(day_itinerary["activities"]) > 3:
            summary += f" + {len(day_itinerary['activities']) - 3} more"
        return summary
