from typing import Dict, List, Any, Optional
from datetime import datetime
from app.core.logger import setup_logger

logger = setup_logger(__name__)

class FavoritesService:
    """Manage user favorites and bookmarks"""
    
    def __init__(self):
        self.favorites: Dict[str, List[Dict[str, Any]]] = {}
    
    def add_favorite(
        self,
        user_id: str,
        item_id: str,
        item_type: str,
        item_data: Dict[str, Any]
    ) -> bool:
        """Add item to favorites"""
        try:
            if user_id not in self.favorites:
                self.favorites[user_id] = []
            
            favorite = {
                "id": item_id,
                "type": item_type,
                "data": item_data,
                "added_at": datetime.now().isoformat()
            }
            
            # Check if already favorited
            if not any(f["id"] == item_id for f in self.favorites[user_id]):
                self.favorites[user_id].append(favorite)
                logger.info(f"Added favorite for user {user_id}: {item_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error adding favorite: {e}")
            return False
    
    def remove_favorite(self, user_id: str, item_id: str) -> bool:
        """Remove item from favorites"""
        try:
            if user_id in self.favorites:
                self.favorites[user_id] = [
                    f for f in self.favorites[user_id] if f["id"] != item_id
                ]
                logger.info(f"Removed favorite for user {user_id}: {item_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing favorite: {e}")
            return False
    
    def get_favorites(self, user_id: str, item_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get user favorites"""
        if user_id not in self.favorites:
            return []
        
        favorites = self.favorites[user_id]
        
        if item_type:
            favorites = [f for f in favorites if f["type"] == item_type]
        
        return sorted(favorites, key=lambda x: x["added_at"], reverse=True)
    
    def is_favorite(self, user_id: str, item_id: str) -> bool:
        """Check if item is favorited"""
        if user_id not in self.favorites:
            return False
        return any(f["id"] == item_id for f in self.favorites[user_id])
    
    def get_favorite_count(self, user_id: str) -> int:
        """Get count of user favorites"""
        return len(self.favorites.get(user_id, []))
