from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import logging

from app.config import settings
from app.database import get_db
from app.models.user import User

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()

class AuthMiddleware:
    """Authentication middleware for FastAPI"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        # Skip auth for certain paths
        if scope["type"] == "http":
            path = scope["path"]
            if path in ["/health", "/docs", "/redoc", "/openapi.json"]:
                await self.app(scope, receive, send)
                return
        
        await self.app(scope, receive, send)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError as e:
        logger.error(f"JWT verification failed: {e}")
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    try:
        token = credentials.credentials
        payload = verify_token(token)
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        if not user.is_active:
            raise HTTPException(status_code=401, detail="User account is deactivated")
        
        return user
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def require_role(required_roles: list):
    """Decorator to require specific user roles"""
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

def require_subscription(min_tier: str = "free"):
    """Decorator to require subscription tier"""
    def subscription_checker(current_user: User = Depends(get_current_user)):
        # Define tier hierarchy
        tier_hierarchy = {
            "free": 0,
            "premium": 1,
            "religious": 2,
            "healthcare": 3,
            "other": 2
        }
        
        user_tier_level = tier_hierarchy.get(current_user.subscription_tier, 0)
        required_tier_level = tier_hierarchy.get(min_tier, 0)
        
        if user_tier_level < required_tier_level:
            raise HTTPException(
                status_code=403,
                detail=f"Subscription tier {min_tier} or higher required"
            )
        
        # Check if subscription is expired
        if current_user.subscription_expires_at and current_user.subscription_expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=403,
                detail="Active subscription required"
            )
        
        return current_user
    return subscription_checker

# Convenience functions for common role requirements
require_admin = require_role(["ADMIN", "SUPER_ADMIN"])
require_super_admin = require_role(["SUPER_ADMIN"])
require_premium = require_subscription("premium")
require_religious = require_subscription("religious")
require_healthcare = require_subscription("healthcare")
