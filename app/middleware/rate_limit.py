from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
import logging
from typing import Dict, Tuple
from app.config import settings

logger = logging.getLogger(__name__)

class RateLimitMiddleware:
    """Rate limiting middleware for FastAPI"""
    
    def __init__(self, app):
        self.app = app
        self.requests: Dict[str, Tuple[int, float]] = {}
        self.cleanup_interval = 60  # Clean up every 60 seconds
        self.last_cleanup = time.time()
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Get client identifier
            client_id = self._get_client_id(scope)
            
            # Check rate limit
            if not self._check_rate_limit(client_id):
                # Rate limit exceeded
                response = JSONResponse(
                    status_code=429,
                    content={
                        "success": False,
                        "error": "Rate limit exceeded",
                        "code": "RATE_LIMIT_EXCEEDED",
                        "retry_after": settings.RATE_LIMIT_WINDOW,
                        "limit": settings.RATE_LIMIT_MAX_REQUESTS,
                        "window": settings.RATE_LIMIT_WINDOW
                    }
                )
                
                # Add rate limit headers
                response.headers["Retry-After"] = str(settings.RATE_LIMIT_WINDOW)
                response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_MAX_REQUESTS)
                response.headers["X-RateLimit-Remaining"] = "0"
                response.headers["X-RateLimit-Reset"] = str(int(time.time() + settings.RATE_LIMIT_WINDOW))
                
                await response(scope, receive, send)
                return
            
            # Clean up old entries periodically
            self._cleanup_old_entries()
        
        await self.app(scope, receive, send)
    
    def _get_client_id(self, scope: dict) -> str:
        """Get unique client identifier"""
        # Get client IP
        client_ip = scope.get("client", ("unknown", 0))[0]
        
        # Get user agent if available
        headers = dict(scope.get("headers", []))
        user_agent = headers.get(b"user-agent", b"unknown").decode("utf-8", errors="ignore")
        
        # Create client identifier
        client_id = f"{client_ip}:{user_agent[:50]}"
        return client_id
    
    def _check_rate_limit(self, client_id: str) -> bool:
        """Check if client is within rate limit"""
        current_time = time.time()
        
        if client_id in self.requests:
            request_count, window_start = self.requests[client_id]
            
            # Check if window has expired
            if current_time - window_start > settings.RATE_LIMIT_WINDOW:
                # Reset window
                self.requests[client_id] = (1, current_time)
                return True
            
            # Check if limit exceeded
            if request_count >= settings.RATE_LIMIT_MAX_REQUESTS:
                return False
            
            # Increment request count
            self.requests[client_id] = (request_count + 1, window_start)
        else:
            # First request from this client
            self.requests[client_id] = (1, current_time)
        
        return True
    
    def _cleanup_old_entries(self):
        """Clean up expired rate limit entries"""
        current_time = time.time()
        
        # Only cleanup every cleanup_interval seconds
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        self.last_cleanup = current_time
        
        # Remove expired entries
        expired_clients = []
        for client_id, (_, window_start) in self.requests.items():
            if current_time - window_start > settings.RATE_LIMIT_WINDOW:
                expired_clients.append(client_id)
        
        for client_id in expired_clients:
            del self.requests[client_id]
        
        if expired_clients:
            logger.debug(f"Cleaned up {len(expired_clients)} expired rate limit entries")

# Rate limit decorator for specific endpoints
def rate_limit(max_requests: int = None, window: int = None):
    """Decorator to apply custom rate limiting to endpoints"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # This would be implemented per-endpoint if needed
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Predefined rate limit configurations
RATE_LIMIT_CONFIGS = {
    "auth": {
        "max_requests": 5,
        "window": 900  # 15 minutes
    },
    "upload": {
        "max_requests": 10,
        "window": 60   # 1 minute
    },
    "api": {
        "max_requests": 60,
        "window": 60   # 1 minute
    },
    "public": {
        "max_requests": 100,
        "window": 60   # 1 minute
    }
}
