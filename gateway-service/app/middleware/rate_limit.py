"""
Rate limiting middleware using Redis with MySQL integration
"""

import time
import json
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Callable
from fastapi import Request, HTTPException, status, FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
import redis.asyncio as aioredis
from app.settings import get_settings
from app.utils.rate_limit_storage import RateLimitStorage


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
        # Line 25-26: Added MySQL storage for rate limit records
        # Reason: Integrate MySQL with Redis for persistent rate limit record storage
        #         Redis handles fast rate limit checking, MySQL stores records for audit/analytics
        self.mysql_storage: Optional[RateLimitStorage] = None
        if self.settings.rate_limit_mysql_enabled:
            self.mysql_storage = RateLimitStorage()
            # Line 33-39: Log MySQL storage initialization
            # Reason: Help debug why MySQL storage might not be working
            import logging
            logger = logging.getLogger(__name__)
            logger.info(
                f"MySQL rate limit storage initialized: enabled=True, "
                f"async={self.settings.rate_limit_mysql_async}, "
                f"storage={self.mysql_storage is not None}"
            )
        else:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("MySQL rate limit storage is DISABLED in settings!")
        # Line 37-39: Initialize background tasks set for tracking async MySQL storage tasks
        # Reason: Track background tasks to prevent garbage collection and ensure they complete
        #         This ensures MySQL storage tasks complete even if request finishes quickly
        self._background_tasks: set = set()
    
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
        
        Uses Redis for fast rate limit checking and optionally stores records in MySQL
        for audit and analytics.
        
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
            # Get current count from Redis (fast in-memory check)
            current = await self.redis_client.get(key)
            count = int(current) if current else 0
            
            if count >= limit:
                # Rate limit exceeded - store in MySQL if enabled
                if self.mysql_storage and self.settings.rate_limit_mysql_enabled:
                    await self._store_rate_limit_record_async(
                        identifier, window, route_path, count, window_seconds
                    )
                return False, 0
            
            # Increment and set expiration in Redis
            pipe = self.redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, window_seconds)
            results = await pipe.execute()
            
            new_count = results[0]
            remaining = max(0, limit - new_count)
            
            # Store rate limit record in MySQL if enabled
            # Line 129-150: Store rate limit record in MySQL after Redis update
            # Reason: Persist rate limit records for audit, analytics, and historical tracking
            #         This complements Redis which handles fast rate limit checking
            # Solution: Store records asynchronously to avoid blocking rate limit check
            if self.mysql_storage and self.settings.rate_limit_mysql_enabled:
                # Line 139-150: Call MySQL storage with logging
                # Reason: Add logging to debug why records might not be stored
                import logging
                logger = logging.getLogger(__name__)
                logger.info(
                    f"Storing rate limit record in MySQL: identifier={identifier}, "
                    f"window={window}, count={new_count}, route={route_path}, "
                    f"async={self.settings.rate_limit_mysql_async}"
                )
                try:
                    await self._store_rate_limit_record_async(
                        identifier, window, route_path, new_count, window_seconds
                    )
                    logger.info(f"MySQL storage call completed for identifier={identifier}")
                except Exception as e:
                    logger.error(
                        f"Exception in _store_rate_limit_record_async: {e}",
                        exc_info=True
                    )
            
            return True, remaining
        except Exception as e:
            # If Redis fails, allow request (fail open)
            return True, limit
    
    async def _store_rate_limit_record_async(
        self,
        identifier: str,
        window: str,
        route_path: Optional[str],
        request_count: int,
        window_seconds: int
    ) -> None:
        """
        Store rate limit record in MySQL asynchronously
        
        This method stores rate limit records in MySQL without blocking the rate limit check.
        It calculates window start and end times based on current time and window duration.
        
        Args:
            identifier: Rate limit identifier
            window: Window type (minute, hour, day)
            route_path: Optional route path
            request_count: Current request count
            window_seconds: Window duration in seconds
        """
        # Line 117-145: Async MySQL storage for rate limit records
        # Reason: Store rate limit records in MySQL for audit and analytics
        #         Done asynchronously to avoid blocking rate limit check
        # Solution: Calculate window boundaries and store record in background
        
        if not self.mysql_storage:
            return
        
        try:
            # Calculate window boundaries
            now = datetime.utcnow()
            window_start = now.replace(second=0, microsecond=0)
            
            # Adjust window start based on window type
            if window == "minute":
                window_start = window_start.replace(minute=window_start.minute)
            elif window == "hour":
                window_start = window_start.replace(minute=0)
            elif window == "day":
                window_start = window_start.replace(hour=0, minute=0)
            
            window_end = window_start + timedelta(seconds=window_seconds)
            
            # Store record in MySQL (non-blocking)
            # Line 183-220: Store rate limit record in MySQL with proper error handling
            # Reason: Ensure MySQL storage works correctly and errors are logged
            #         Background tasks need proper error handling to avoid silent failures
            # Solution: Create background task with error handling and logging
            
            async def store_record_with_error_handling():
                """Store record with error handling and logging"""
                import logging
                logger = logging.getLogger(__name__)
                try:
                    logger.debug(
                        f"MySQL storage task started: identifier={identifier}, "
                        f"window={window}, count={request_count}"
                    )
                    result = await self.mysql_storage.store_rate_limit_record(
                        identifier=identifier,
                        window_type=window,
                        request_count=request_count,
                        window_start=window_start,
                        window_end=window_end,
                        route_path=route_path
                    )
                    if result:
                        logger.debug(
                            f"MySQL storage task completed successfully: identifier={identifier}, "
                            f"window={window}, count={request_count}"
                        )
                    else:
                        # Log warning if storage fails (but don't fail rate limiting)
                        logger.warning(
                            f"Failed to store rate limit record in MySQL: "
                            f"identifier={identifier}, window={window}, count={request_count}"
                        )
                except Exception as e:
                    # Log error but don't fail - rate limiting should continue
                    logger.error(
                        f"Error storing rate limit record in MySQL: {e}",
                        exc_info=True
                    )
            
            if self.settings.rate_limit_mysql_async:
                # Create background task with error handling
                # Use asyncio.create_task to run in background
                # Line 238-260: Create background task for MySQL storage
                # Reason: Store rate limit records asynchronously to avoid blocking rate limit check
                #         Task is created and will run in background even after request completes
                # Solution: Create task and let it run - FastAPI/Starlette will ensure it completes
                # Note: Background tasks may not complete if request finishes very quickly.
                #       If records are not appearing in MySQL, try setting RATE_LIMIT_MYSQL_ASYNC=false
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"Creating background task for MySQL storage: identifier={identifier}")
                task = asyncio.create_task(store_record_with_error_handling())
                # Store task reference in a set to prevent garbage collection
                # This ensures the task completes even if request finishes quickly
                if not hasattr(self, '_background_tasks'):
                    self._background_tasks = set()
                self._background_tasks.add(task)
                # Remove task from set when it completes (to prevent memory leak)
                def remove_task(t):
                    self._background_tasks.discard(t)
                    logger.debug(f"Background task completed, {len(self._background_tasks)} remaining")
                task.add_done_callback(remove_task)
                logger.info(f"Background task created and tracked: {len(self._background_tasks)} active tasks")
            else:
                # Synchronous write (for testing or when async is disabled)
                # Line 261-265: Synchronous MySQL storage
                # Reason: Ensures MySQL write completes before continuing
                #         Use this if async mode is not storing records reliably
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"Using synchronous MySQL storage: identifier={identifier}")
                await store_record_with_error_handling()
                logger.info(f"Synchronous MySQL storage completed: identifier={identifier}")
        except Exception as e:
            # If task creation fails, log but don't fail rate limiting
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error creating MySQL storage task: {e}", exc_info=True)
    
    async def check_request_rate_limit(
        self,
        request: Request,
        route_path: Optional[str] = None,
        custom_limit: Optional[int] = None
    ) -> tuple[bool, int]:
        """
        Check rate limit for request
        
        This method extracts user identifier and checks rate limit.
        For login endpoints, it extracts username/email from request body first.
        The request body is preserved for forwarding to backend services.
        
        Args:
            request: FastAPI request object
            route_path: Route path
            custom_limit: Custom rate limit for route
            
        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        # Line 212-240: Rate limit check with identifier extraction
        # Reason: Check rate limit using appropriate identifier
        # Note: Login identifier extraction is done in middleware dispatch
        #       to avoid interfering with request body forwarding
        
        # Get identifier (user_id, login identifier, API key, or IP)
        # Login identifier should already be extracted in middleware if needed
        identifier = self._get_identifier(request)
        
        # Use custom limit or default
        limit = custom_limit or self.settings.rate_limit_per_minute
        window_seconds = 60  # Rate limit window in seconds (1 minute)
        
        return await self.check_rate_limit(identifier, limit, window_seconds, route_path)
    
    async def _extract_login_identifier(self, request: Request) -> Optional[str]:
        """
        Extract user identifier from login request body
        
        This method reads the request body to extract username or email for login endpoints.
        This ensures per-user rate limiting even before authentication completes.
        The body is stored in request.state._body for later use.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Username or email if found, None otherwise
        """
        # Line 138-180: Extract login identifier from request body
        # Reason: For login endpoints, user_id is not available before authentication
        #         We need to extract username/email from request body to enable per-user rate limiting
        # Root Cause: Rate limiting was falling back to IP address for login endpoints,
        #             causing all users from same IP to share rate limit
        # Solution: Extract username/email from request body and use it as identifier
        # Note: Request body is stored in request.state._body so it can be read again later
        
        try:
            # Check if this is a login/register endpoint
            path = request.url.path.lower()
            if "/auth/login" not in path and "/auth/register" not in path:
                return None
            
            # Try to get body from request state (if already read)
            if hasattr(request.state, "login_identifier"):
                return request.state.login_identifier
            
            # Check if body has already been read and stored
            if hasattr(request.state, "_body"):
                body = request.state._body
            else:
                # Read request body and store it for later use
                # Note: request.body() can only be called once in Starlette/FastAPI
                # We need to read it here and store it so it can be reused for forwarding
                try:
                    # Read the body stream
                    body = await request.body()
                    # Store body in request state so it can be read again later
                    # This is critical - without this, the body stream is consumed and lost
                    request.state._body = body
                except Exception:
                    # If body reading fails, return None
                    # This might happen if body was already consumed or doesn't exist
                    return None
            
            if not body:
                return None
            
            # Parse JSON body
            try:
                body_data = json.loads(body.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                return None
            
            # Extract username or email
            username = body_data.get("username") or body_data.get("user_name") or body_data.get("user")
            email = body_data.get("email") or body_data.get("email_address")
            
            # Return first available identifier
            if username:
                request.state.login_identifier = username
                return username
            if email:
                request.state.login_identifier = email
                return email
            
            return None
        except Exception:
            # If extraction fails, return None (will fall back to IP)
            return None
    
    def _get_identifier(self, request: Request) -> str:
        """
        Get rate limit identifier from request
        
        This method extracts user identifier from request to ensure per-user rate limiting.
        Priority order:
        1. user_id from request.state (set after authentication)
        2. login_identifier from request.state (extracted from login request body)
        3. API key from headers
        4. IP address (fallback, but should be avoided for authenticated requests)
        
        Args:
            request: FastAPI request object
            
        Returns:
            Identifier string in format: "user:{user_id}", "login:{username}", "api_key:{key}", or "ip:{ip}"
        """
        # Line 172-210: Enhanced identifier extraction for per-user rate limiting
        # Reason: Fix issue where rate limiting was shared across users
        # Root Cause: For login endpoints, user_id is not available before authentication,
        #             causing fallback to IP address which is shared by multiple users
        # Solution: Extract username/email from request body for login endpoints and store in request.state
        
        # Priority 1: Try to get user_id from context (set after authentication)
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"
        
        # Priority 2: Try login identifier (extracted from request body for login endpoints)
        login_identifier = getattr(request.state, "login_identifier", None)
        if login_identifier:
            return f"login:{login_identifier}"
        
        # Priority 3: Try API key
        api_key = request.headers.get(get_settings().api_key_header)
        if api_key:
            return f"api_key:{api_key}"
        
        # Priority 4: Fall back to IP address (should be avoided for authenticated requests)
        # For login endpoints, this should not happen if login_identifier extraction works
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"
    
    async def dispatch(self, request: Request, call_next: Callable) -> any:
        """
        Middleware execution
        
        This middleware handles rate limiting. For login endpoints, it extracts
        the username/email from the request body before rate limiting to ensure
        per-user rate limiting.
        
        Args:
            request: FastAPI request object
            call_next: Next middleware or route handler
            
        Returns:
            Response
        """
        # Line 272-295: Middleware dispatch with body preservation
        # Reason: Extract login identifier from body for rate limiting
        #         Body must be preserved for forwarding to backend services
        # Solution: Read body only for login endpoints and store it for reuse
        
        # For login endpoints, extract identifier from body before rate limiting
        # This ensures per-user rate limiting even before authentication
        path = request.url.path.lower()
        if "/auth/login" in path or "/auth/register" in path:
            # Extract login identifier and preserve body
            await self._extract_login_identifier(request)
        
        # Rate limiting is handled per-route in the route handler
        # The middleware just prepares the identifier if needed
        response = await call_next(request)
        
        # Add rate limit headers
        if hasattr(request.state, "rate_limit_remaining"):
            response.headers["X-RateLimit-Remaining"] = str(request.state.rate_limit_remaining)
        
        return response

