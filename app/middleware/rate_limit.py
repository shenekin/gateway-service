"""
Rate limiting middleware using Redis
"""

import time
from typing import Optional, Callable
from fastapi import Request, HTTPException, status, FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
import redis.asyncio as aioredis
from app.settings import get_settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using token bucket algorithm"""
    
    def __init__(self, app: FastAPI):
        """Initialize rate limiting middleware
        
        Args:
            app: FastAPI application instance
        """
        super().__init__(app)
        self.settings = get_settings()
        self.redis_client: Optional[aioredis.Redis] = None
    
    async def connect_redis(self) -> None:
        """Connect to Redis"""
        if not self.redis_client:
            self.redis_client = await aioredis.from_url(
                f"redis://{self.settings.redis_host}:{self.settings.redis_port}",
                password=self.settings.redis_password,
                db=self.settings.redis_db,
                decode_responses=True
            )
    
    async def close_redis(self) -> None:
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.aclose()
            self.redis_client = None
    
    def _get_rate_limit_key(
        self,
        identifier: str,
        window: str,
        route_path: Optional[str] = None
    ) -> str:
        """
        Generate rate limit key
        
        Args:
            identifier: User ID, IP, or API key
            window: Time window (minute, hour, day)
            route_path: Optional route path
            
        Returns:
            Redis key string
        """
        if route_path:
            return f"rate_limit:{identifier}:{window}:{route_path}"
        return f"rate_limit:{identifier}:{window}"
    
    async def check_rate_limit(
        self,
        identifier: str,
        limit: int,
        window_seconds: int,
        route_path: Optional[str] = None
    ) -> tuple[bool, int]:
        """
        Check if request is within rate limit
        
        Args:
            identifier: User ID, IP, or API key
            limit: Maximum requests allowed
            window_seconds: Time window in seconds
            route_path: Optional route path
            
        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        if not self.settings.rate_limit_enabled:
            return True, limit
        
        await self.connect_redis()
        
        window = "minute" if window_seconds == 60 else "hour" if window_seconds == 3600 else "day"
        key = self._get_rate_limit_key(identifier, window, route_path)
        
        try:
            # Get current count
            current = await self.redis_client.get(key)
            count = int(current) if current else 0
            
            if count >= limit:
                return False, 0
            
            # Increment and set expiration
            pipe = self.redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, window_seconds)
            results = await pipe.execute()
            
            new_count = results[0]
            remaining = max(0, limit - new_count)
            
            return True, remaining
        except Exception as e:
            # If Redis fails, allow request (fail open)
            return True, limit
    
    async def check_request_rate_limit(
        self,
        request: Request,
        route_path: Optional[str] = None,
        custom_limit: Optional[int] = None
    ) -> tuple[bool, int]:
        """
        Check rate limit for request
        
        Args:
            request: FastAPI request object
            route_path: Route path
            custom_limit: Custom rate limit for route
            
        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        # Get identifier (user_id, IP, or API key)
        identifier = self._get_identifier(request)
        
        # Use custom limit or default
        limit = custom_limit or self.settings.rate_limit_per_minute
        window_seconds = 60
        
        return await self.check_rate_limit(identifier, limit, window_seconds, route_path)
    
    def _get_identifier(self, request: Request) -> str:
        """
        Get rate limit identifier from request
        
        Args:
            request: FastAPI request object
            
        Returns:
            Identifier string
        """
        # Try to get user_id from context
        user_id = request.state.get("user_id")
        if user_id:
            return f"user:{user_id}"
        
        # Try API key
        api_key = request.headers.get(get_settings().api_key_header)
        if api_key:
            return f"api_key:{api_key}"
        
        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"
    
    async def dispatch(self, request: Request, call_next: Callable) -> any:
        """
        Middleware execution
        
        Args:
            request: FastAPI request object
            call_next: Next middleware or route handler
            
        Returns:
            Response
        """
        # Rate limiting is handled per-route
        response = await call_next(request)
        
        # Add rate limit headers
        if hasattr(request.state, "rate_limit_remaining"):
            response.headers["X-RateLimit-Remaining"] = str(request.state.rate_limit_remaining)
        
        return response

