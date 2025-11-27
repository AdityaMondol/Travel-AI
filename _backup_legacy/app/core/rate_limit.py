"""Rate limiting and quota management"""
from typing import Dict, Tuple
from datetime import datetime, timedelta
from app.core.config import get_config
from app.core.logger import setup_logger


logger = setup_logger(__name__)


class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self):
        self.config = get_config()
        self.buckets: Dict[str, list] = {}
    
    def is_allowed(self, user_id: str) -> Tuple[bool, Dict[str, any]]:
        """Check if request is allowed"""
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self.config.rate_limit_window_seconds)
        
        if user_id not in self.buckets:
            self.buckets[user_id] = []
        
        # Remove old requests outside window
        self.buckets[user_id] = [
            ts for ts in self.buckets[user_id]
            if ts > window_start
        ]
        
        # Check limit
        if len(self.buckets[user_id]) >= self.config.rate_limit_requests:
            return False, {
                "limit": self.config.rate_limit_requests,
                "window_seconds": self.config.rate_limit_window_seconds,
                "current": len(self.buckets[user_id]),
            }
        
        # Add current request
        self.buckets[user_id].append(now)
        
        return True, {
            "limit": self.config.rate_limit_requests,
            "remaining": self.config.rate_limit_requests - len(self.buckets[user_id]),
            "reset_in_seconds": (
                self.buckets[user_id][0] + 
                timedelta(seconds=self.config.rate_limit_window_seconds) - now
            ).total_seconds(),
        }


class QuotaManager:
    """Manage user quotas"""
    
    def __init__(self):
        self.config = get_config()
        self.user_costs: Dict[str, float] = {}
    
    def check_quota(self, user_id: str, cost: float) -> Tuple[bool, Dict[str, any]]:
        """Check if user has quota"""
        from app.core.auth import get_auth_manager
        
        auth = get_auth_manager()
        user = auth.get_user(user_id)
        
        if not user:
            return False, {"error": "User not found"}
        
        if (user.quota_used_usd + cost) > user.quota_monthly_usd:
            return False, {
                "quota_limit": user.quota_monthly_usd,
                "quota_used": user.quota_used_usd,
                "requested_cost": cost,
                "remaining": user.quota_monthly_usd - user.quota_used_usd,
            }
        
        return True, {
            "quota_limit": user.quota_monthly_usd,
            "quota_used": user.quota_used_usd + cost,
            "remaining": user.quota_monthly_usd - (user.quota_used_usd + cost),
        }
    
    def deduct_quota(self, user_id: str, cost: float) -> bool:
        """Deduct from user quota"""
        from app.core.auth import get_auth_manager
        
        auth = get_auth_manager()
        return auth.deduct_quota(user_id, cost)


# Global instances
_rate_limiter: RateLimiter = None
_quota_manager: QuotaManager = None


def get_rate_limiter() -> RateLimiter:
    """Get rate limiter"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


def get_quota_manager() -> QuotaManager:
    """Get quota manager"""
    global _quota_manager
    if _quota_manager is None:
        _quota_manager = QuotaManager()
    return _quota_manager
