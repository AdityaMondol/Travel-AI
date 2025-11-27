"""Authentication and authorization"""
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from enum import Enum
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from app.core.config import get_config
from app.core.logger import setup_logger


logger = setup_logger(__name__)


class UserRole(str, Enum):
    """User roles"""
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"
    API = "api"


class User(BaseModel):
    """User model"""
    id: str
    username: str
    email: str
    role: UserRole
    is_active: bool = True
    quota_monthly_usd: float = 100.0
    quota_used_usd: float = 0.0


class APIKey(BaseModel):
    """API key model"""
    key_id: str
    user_id: str
    key_hash: str
    created_at: datetime
    last_used: Optional[datetime] = None
    is_active: bool = True


class AuthManager:
    """Authentication and authorization manager"""
    
    def __init__(self):
        self.config = get_config()
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.users: Dict[str, User] = {}
        self.api_keys: Dict[str, APIKey] = {}
    
    def hash_password(self, password: str) -> str:
        """Hash password"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain: str, hashed: str) -> bool:
        """Verify password"""
        return self.pwd_context.verify(plain, hashed)
    
    def create_access_token(self, user_id: str, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        if expires_delta is None:
            expires_delta = timedelta(hours=self.config.jwt_expiration_hours)
        
        expire = datetime.utcnow() + expires_delta
        
        payload = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
        }
        
        token = jwt.encode(
            payload,
            self.config.secret_key,
            algorithm=self.config.jwt_algorithm
        )
        
        return token
    
    def verify_token(self, token: str) -> Optional[str]:
        """Verify JWT token and return user_id"""
        try:
            payload = jwt.decode(
                token,
                self.config.secret_key,
                algorithms=[self.config.jwt_algorithm]
            )
            user_id = payload.get("sub")
            return user_id
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
    
    def create_user(
        self,
        user_id: str,
        username: str,
        email: str,
        role: UserRole = UserRole.VIEWER,
        quota_monthly_usd: float = 100.0
    ) -> User:
        """Create user"""
        user = User(
            id=user_id,
            username=username,
            email=email,
            role=role,
            quota_monthly_usd=quota_monthly_usd
        )
        self.users[user_id] = user
        logger.info(f"User created: {username}")
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user"""
        return self.users.get(user_id)
    
    def create_api_key(self, user_id: str) -> str:
        """Create API key for user"""
        import secrets
        import hashlib
        
        key = secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        
        api_key = APIKey(
            key_id=secrets.token_hex(8),
            user_id=user_id,
            key_hash=key_hash,
            created_at=datetime.utcnow()
        )
        
        self.api_keys[api_key.key_id] = api_key
        logger.info(f"API key created for user: {user_id}")
        
        return key
    
    def verify_api_key(self, key: str) -> Optional[str]:
        """Verify API key and return user_id"""
        import hashlib
        
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        
        for api_key in self.api_keys.values():
            if api_key.key_hash == key_hash and api_key.is_active:
                api_key.last_used = datetime.utcnow()
                return api_key.user_id
        
        return None
    
    def check_quota(self, user_id: str, cost: float) -> bool:
        """Check if user has quota for cost"""
        user = self.get_user(user_id)
        if not user:
            return False
        
        return (user.quota_used_usd + cost) <= user.quota_monthly_usd
    
    def deduct_quota(self, user_id: str, cost: float) -> bool:
        """Deduct from user quota"""
        user = self.get_user(user_id)
        if not user:
            return False
        
        if not self.check_quota(user_id, cost):
            logger.warning(f"Quota exceeded for user: {user_id}")
            return False
        
        user.quota_used_usd += cost
        return True


# Global auth manager
_auth_manager: Optional[AuthManager] = None


def get_auth_manager() -> AuthManager:
    """Get auth manager"""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
    return _auth_manager
