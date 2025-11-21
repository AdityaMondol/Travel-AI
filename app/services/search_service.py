from typing import Dict, List, Any, Optional
from app.core.logger import setup_logger

logger = setup_logger(__name__)

class SearchService:
    """Search and filter travel data"""
    
    @staticmethod
    def search_places(
        places: List[Dict[str, Any]],
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search places by name or description"""
        query_lower = query.lower()
        results = [
            place for place in places
            if query_lower in place.get("name", "").lower() or
               query_lower in place.get("description", "").lower()
        ]
        return results[:limit]
    
    @staticmethod
    def filter_by_category(
        places: List[Dict[str, Any]],
        category: str
    ) -> List[Dict[str, Any]]:
        """Filter places by category"""
        return [
            place for place in places
            if place.get("category", "").lower() == category.lower()
        ]
    
    @staticmethod
    def sort_places(
        places: List[Dict[str, Any]],
        sort_by: str = "rating"
    ) -> List[Dict[str, Any]]:
        """Sort places by various criteria"""
        if sort_by == "rating":
            return sorted(places, key=lambda x: x.get("rating", 0), reverse=True)
        elif sort_by == "distance":
            return sorted(places, key=lambda x: x.get("distance", float('inf')))
        elif sort_by == "name":
            return sorted(places, key=lambda x: x.get("name", ""))
        return places
    
    @staticmethod
    def search_restaurants(
        restaurants: List[Dict[str, Any]],
        cuisine: Optional[str] = None,
        price_range: Optional[str] = None,
        rating_min: float = 0
    ) -> List[Dict[str, Any]]:
        """Search restaurants with filters"""
        results = restaurants
        
        if cuisine:
            results = [
                r for r in results
                if cuisine.lower() in r.get("cuisine", "").lower()
            ]
        
        if price_range:
            results = [
                r for r in results
                if r.get("price_range", "") == price_range
            ]
        
        results = [
            r for r in results
            if r.get("rating", 0) >= rating_min
        ]
        
        return results
    
    @staticmethod
    def get_nearby_places(
        places: List[Dict[str, Any]],
        latitude: float,
        longitude: float,
        radius_km: float = 5
    ) -> List[Dict[str, Any]]:
        """Get places within radius (simplified - no actual distance calculation)"""
        return [
            place for place in places
            if place.get("latitude") and place.get("longitude")
        ][:10]
