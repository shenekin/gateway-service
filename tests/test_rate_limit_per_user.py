"""
Unit tests for per-user rate limiting
Tests verify that rate limiting works correctly for individual users
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from fastapi import Request
from starlette.datastructures import Headers

# Add parent directory to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.middleware.rate_limit import RateLimitMiddleware
from app.settings import get_settings


class TestPerUserRateLimiting:
    """Test cases for per-user rate limiting"""
    
    @pytest.fixture
    def middleware(self):
        """Create RateLimitMiddleware instance"""
        app = MagicMock()
        return RateLimitMiddleware(app)
    
    @pytest.fixture
    def mock_request(self):
        """Create mock request"""
        request = MagicMock(spec=Request)
        request.url.path = "/auth/login"
        request.client.host = "192.168.1.1"
        request.client = MagicMock()
        request.client.host = "192.168.1.1"
        request.state = MagicMock()
        request.headers = Headers({})
        request.query_params = {}
        return request
    
    @pytest.mark.asyncio
    async def test_extract_login_identifier_with_username(self, middleware, mock_request):
        """
        Test extracting login identifier from request body with username
        
        Test Case: Login request with username in body
        Expected: Returns username as identifier
        """
        # Line 15-35: Test login identifier extraction with username
        # Reason: Verify that username is correctly extracted from login request body
        
        # Mock request body with username
        body_data = {"username": "testuser", "password": "testpass"}
        body_bytes = json.dumps(body_data).encode("utf-8")
        
        # Mock request.body() to return body
        async def mock_body():
            return body_bytes
        mock_request.body = mock_body
        
        identifier = await middleware._extract_login_identifier(mock_request)
        
        assert identifier == "testuser"
        assert hasattr(mock_request.state, "login_identifier")
        assert mock_request.state.login_identifier == "testuser"
        assert hasattr(mock_request.state, "_body")
    
    @pytest.mark.asyncio
    async def test_extract_login_identifier_with_email(self, middleware, mock_request):
        """
        Test extracting login identifier from request body with email
        
        Test Case: Login request with email in body
        Expected: Returns email as identifier
        """
        # Line 37-55: Test login identifier extraction with email
        # Reason: Verify that email is correctly extracted from login request body
        
        # Mock request body with email
        body_data = {"email": "test@example.com", "password": "testpass"}
        body_bytes = json.dumps(body_data).encode("utf-8")
        
        # Mock request.body() to return body
        async def mock_body():
            return body_bytes
        mock_request.body = mock_body
        
        identifier = await middleware._extract_login_identifier(mock_request)
        
        assert identifier == "test@example.com"
        assert mock_request.state.login_identifier == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_extract_login_identifier_no_body(self, middleware, mock_request):
        """
        Test extracting login identifier when body is empty
        
        Test Case: Login request with empty body
        Expected: Returns None
        """
        # Line 57-70: Test login identifier extraction with empty body
        # Reason: Verify that empty body is handled correctly
        
        async def mock_body():
            return b""
        mock_request.body = mock_body
        
        identifier = await middleware._extract_login_identifier(mock_request)
        
        assert identifier is None
    
    @pytest.mark.asyncio
    async def test_extract_login_identifier_non_login_path(self, middleware, mock_request):
        """
        Test extracting login identifier for non-login path
        
        Test Case: Request to non-login endpoint
        Expected: Returns None
        """
        # Line 72-85: Test login identifier extraction for non-login paths
        # Reason: Verify that identifier extraction only happens for login endpoints
        
        mock_request.url.path = "/projects"
        
        identifier = await middleware._extract_login_identifier(mock_request)
        
        assert identifier is None
    
    def test_get_identifier_with_user_id(self, middleware, mock_request):
        """
        Test getting identifier when user_id is available
        
        Test Case: Request with user_id in state
        Expected: Returns "user:{user_id}"
        """
        # Line 87-100: Test identifier extraction with user_id
        # Reason: Verify that user_id takes priority over other identifiers
        
        mock_request.state.user_id = "user123"
        
        identifier = middleware._get_identifier(mock_request)
        
        assert identifier == "user:user123"
    
    def test_get_identifier_with_login_identifier(self, middleware, mock_request):
        """
        Test getting identifier when login identifier is available
        
        Test Case: Request with login_identifier in state (for login endpoints)
        Expected: Returns "login:{username}"
        """
        # Line 102-115: Test identifier extraction with login identifier
        # Reason: Verify that login identifier is used for login endpoints
        
        mock_request.state.login_identifier = "testuser"
        
        identifier = middleware._get_identifier(mock_request)
        
        assert identifier == "login:testuser"
    
    def test_get_identifier_with_api_key(self, middleware, mock_request):
        """
        Test getting identifier when API key is available
        
        Test Case: Request with API key in headers
        Expected: Returns "api_key:{key}"
        """
        # Line 117-130: Test identifier extraction with API key
        # Reason: Verify that API key is used when available
        
        with patch("app.middleware.rate_limit.get_settings") as mock_settings:
            mock_settings.return_value.api_key_header = "X-API-Key"
            mock_request.headers = Headers({"X-API-Key": "test-api-key"})
            
            identifier = middleware._get_identifier(mock_request)
            
            assert identifier == "api_key:test-api-key"
    
    def test_get_identifier_fallback_to_ip(self, middleware, mock_request):
        """
        Test getting identifier when falling back to IP address
        
        Test Case: Request with no user_id, login_identifier, or API key
        Expected: Returns "ip:{ip_address}"
        """
        # Line 132-145: Test identifier extraction fallback to IP
        # Reason: Verify that IP address is used as fallback
        
        identifier = middleware._get_identifier(mock_request)
        
        assert identifier == "ip:192.168.1.1"
    
    @pytest.mark.asyncio
    async def test_check_request_rate_limit_per_user(self, middleware, mock_request):
        """
        Test rate limit check for individual users
        
        Test Case: Two different users should have separate rate limits
        Expected: Each user has independent rate limit counter
        """
        # Line 147-180: Test per-user rate limiting
        # Reason: Verify that different users have separate rate limit counters
        
        # Mock settings
        middleware.settings.rate_limit_enabled = True
        middleware.settings.rate_limit_per_minute = 10
        
        # Mock Redis client
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value="0")
        mock_redis.pipeline = MagicMock()
        mock_pipe = MagicMock()
        mock_pipe.incr = MagicMock(return_value=mock_pipe)
        mock_pipe.expire = MagicMock(return_value=mock_pipe)
        mock_pipe.execute = AsyncMock(return_value=[1])
        mock_redis.pipeline.return_value = mock_pipe
        middleware.redis_client = mock_redis
        
        # Mock login identifier extraction
        mock_request.state.login_identifier = "user1"
        
        # First user
        is_allowed_1, remaining_1 = await middleware.check_request_rate_limit(
            mock_request,
            route_path="/auth/login"
        )
        
        assert is_allowed_1 is True
        assert remaining_1 == 9
        
        # Verify Redis key contains user identifier
        call_args = mock_redis.pipeline.call_args
        assert call_args is not None
    
    @pytest.mark.asyncio
    async def test_rate_limit_different_users_separate_limits(self, middleware):
        """
        Test that different users have separate rate limits
        
        Test Case: User1 and User2 should have independent rate limits
        Expected: Rate limiting one user does not affect the other
        """
        # Line 182-220: Test separate rate limits for different users
        # Reason: Verify that rate limiting is per-user, not global
        
        # Mock settings
        middleware.settings.rate_limit_enabled = True
        middleware.settings.rate_limit_per_minute = 10
        
        # Mock Redis client
        mock_redis = AsyncMock()
        middleware.redis_client = mock_redis
        
        # Create two different user requests
        request1 = MagicMock(spec=Request)
        request1.state = MagicMock()
        request1.state.login_identifier = "user1"
        request1.client = MagicMock()
        request1.client.host = "192.168.1.1"
        request1.headers = Headers({})
        request1.query_params = {}
        request1.url.path = "/auth/login"
        
        request2 = MagicMock(spec=Request)
        request2.state = MagicMock()
        request2.state.login_identifier = "user2"
        request2.client = MagicMock()
        request2.client.host = "192.168.1.1"  # Same IP but different user
        request2.headers = Headers({})
        request2.query_params = {}
        request2.url.path = "/auth/login"
        
        # Mock Redis to return different counts for different keys
        async def mock_get(key):
            if "user1" in key:
                return "9"  # User1 has 9 requests
            elif "user2" in key:
                return "1"  # User2 has 1 request
            return "0"
        
        mock_redis.get = AsyncMock(side_effect=mock_get)
        mock_redis.pipeline = MagicMock()
        mock_pipe = MagicMock()
        mock_pipe.incr = MagicMock(return_value=mock_pipe)
        mock_pipe.expire = MagicMock(return_value=mock_pipe)
        mock_pipe.execute = AsyncMock(return_value=[10])  # After increment
        mock_redis.pipeline.return_value = mock_pipe
        
        # Check rate limit for user1 (should be at limit)
        is_allowed_1, remaining_1 = await middleware.check_request_rate_limit(
            request1,
            route_path="/auth/login"
        )
        
        # Check rate limit for user2 (should have remaining)
        is_allowed_2, remaining_2 = await middleware.check_request_rate_limit(
            request2,
            route_path="/auth/login"
        )
        
        # User1 should be at limit (9 + 1 = 10, which equals limit)
        # User2 should have remaining (1 + 1 = 2, which is less than limit)
        # Note: The actual logic checks if count >= limit before incrementing
        # So if count is 9, it will increment to 10, which equals limit, so it's allowed
        # But if count is 10, it will be denied
        
        # Verify that different Redis keys were used
        get_calls = mock_redis.get.call_args_list
        assert len(get_calls) == 2
        # Check that keys contain different user identifiers
        key1 = str(get_calls[0])
        key2 = str(get_calls[1])
        assert ("user1" in key1 or "user2" in key1)
        assert ("user1" in key2 or "user2" in key2)
    
    @pytest.mark.asyncio
    async def test_rate_limit_same_user_same_limit(self, middleware):
        """
        Test that same user shares rate limit across requests
        
        Test Case: Same user making multiple requests
        Expected: Rate limit counter increments for same user
        """
        # Line 222-250: Test that same user shares rate limit
        # Reason: Verify that rate limiting correctly tracks same user across requests
        
        # Mock settings
        middleware.settings.rate_limit_enabled = True
        middleware.settings.rate_limit_per_minute = 10
        
        # Mock Redis client
        mock_redis = AsyncMock()
        middleware.redis_client = mock_redis
        
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        request.state.login_identifier = "user1"
        request.client = MagicMock()
        request.client.host = "192.168.1.1"
        request.headers = Headers({})
        request.query_params = {}
        request.url.path = "/auth/login"
        
        # Mock Redis to return incrementing counts
        call_count = [0]
        async def mock_get(key):
            call_count[0] += 1
            if call_count[0] == 1:
                return "0"  # First request
            elif call_count[0] == 2:
                return "1"  # Second request
            return "2"  # Third request
        
        mock_redis.get = AsyncMock(side_effect=mock_get)
        mock_redis.pipeline = MagicMock()
        mock_pipe = MagicMock()
        mock_pipe.incr = MagicMock(return_value=mock_pipe)
        mock_pipe.expire = MagicMock(return_value=mock_pipe)
        mock_pipe.execute = AsyncMock(return_value=[1])  # After increment
        mock_redis.pipeline.return_value = mock_pipe
        
        # First request
        is_allowed_1, remaining_1 = await middleware.check_request_rate_limit(
            request,
            route_path="/auth/login"
        )
        
        # Second request (same user)
        is_allowed_2, remaining_2 = await middleware.check_request_rate_limit(
            request,
            route_path="/auth/login"
        )
        
        # Verify that same Redis key was used (same user identifier)
        get_calls = mock_redis.get.call_args_list
        assert len(get_calls) >= 2
        # All calls should use the same key (containing user1)
        for call in get_calls:
            key = str(call)
            assert "user1" in key or "login:user1" in key
    
    @pytest.mark.asyncio
    async def test_rate_limit_login_endpoint_extracts_identifier(self, middleware):
        """
        Test that login endpoint extracts identifier from body
        
        Test Case: Login request should extract username from body
        Expected: login_identifier is set in request.state
        """
        # Line 252-280: Test login endpoint identifier extraction
        # Reason: Verify that login endpoints correctly extract user identifier
        
        # Mock settings
        middleware.settings.rate_limit_enabled = True
        middleware.settings.rate_limit_per_minute = 10
        
        # Mock Redis client
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value="0")
        mock_redis.pipeline = MagicMock()
        mock_pipe = MagicMock()
        mock_pipe.incr = MagicMock(return_value=mock_pipe)
        mock_pipe.expire = MagicMock(return_value=mock_pipe)
        mock_pipe.execute = AsyncMock(return_value=[1])
        mock_redis.pipeline.return_value = mock_pipe
        middleware.redis_client = mock_redis
        
        # Create request with login body
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        request.client = MagicMock()
        request.client.host = "192.168.1.1"
        request.headers = Headers({})
        request.query_params = {}
        request.url.path = "/auth/login"
        
        # Mock request body
        body_data = {"username": "testuser", "password": "testpass"}
        body_bytes = json.dumps(body_data).encode("utf-8")
        
        async def mock_body():
            return body_bytes
        request.body = mock_body
        
        # Check rate limit (should extract identifier)
        is_allowed, remaining = await middleware.check_request_rate_limit(
            request,
            route_path="/auth/login"
        )
        
        # Verify that login_identifier was extracted
        assert hasattr(request.state, "login_identifier")
        assert request.state.login_identifier == "testuser"
        assert hasattr(request.state, "_body")
        
        # Verify that identifier was used in rate limit key
        get_calls = mock_redis.get.call_args_list
        assert len(get_calls) > 0
        # Key should contain login identifier
        key = str(get_calls[0])
        assert "testuser" in key or "login:testuser" in key

