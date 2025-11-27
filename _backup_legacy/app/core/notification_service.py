from typing import Dict, List, Any, Optional
from datetime import datetime
from app.core.logger import setup_logger

logger = setup_logger(__name__)

class NotificationService:
    """Handle notifications and alerts"""
    
    def __init__(self):
        self.notifications: List[Dict[str, Any]] = []
        self.subscribers: Dict[str, List[callable]] = {}
    
    def create_notification(
        self,
        title: str,
        message: str,
        notification_type: str = "info",
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a notification"""
        notification = {
            "id": len(self.notifications) + 1,
            "title": title,
            "message": message,
            "type": notification_type,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "read": False
        }
        self.notifications.append(notification)
        self._trigger_subscribers(notification_type, notification)
        logger.info(f"Notification created: {title}")
        return notification
    
    def subscribe(self, event_type: str, callback: callable) -> None:
        """Subscribe to notification events"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
    
    def _trigger_subscribers(self, event_type: str, data: Dict[str, Any]) -> None:
        """Trigger all subscribers for event type"""
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"Subscriber callback error: {e}")
    
    def get_notifications(self, user_id: Optional[str] = None, unread_only: bool = False) -> List[Dict[str, Any]]:
        """Get notifications for user"""
        notifications = self.notifications
        
        if user_id:
            notifications = [n for n in notifications if n.get("user_id") == user_id]
        
        if unread_only:
            notifications = [n for n in notifications if not n.get("read")]
        
        return sorted(notifications, key=lambda x: x["timestamp"], reverse=True)
    
    def mark_as_read(self, notification_id: int) -> bool:
        """Mark notification as read"""
        for notification in self.notifications:
            if notification["id"] == notification_id:
                notification["read"] = True
                return True
        return False
    
    def clear_notifications(self, user_id: Optional[str] = None) -> int:
        """Clear notifications"""
        if user_id:
            initial_count = len(self.notifications)
            self.notifications = [n for n in self.notifications if n.get("user_id") != user_id]
            return initial_count - len(self.notifications)
        else:
            count = len(self.notifications)
            self.notifications.clear()
            return count
