"""
Unit tests for TokenManager

Tests cover:
- Refresh token storage in Redis
- Token validation
- Token rotation
- Token revocation
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from app.utils.token_manager import TokenManager
from app.settings import get_settings


@pytest.fixture
def token_manager():
    """Create TokenManager instance"""
    return TokenManager()


@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    redis_mock = AsyncMock()
    redis_mock.get = AsyncMock(return_value=None)
    redis_mock.setex = AsyncMock(return_value=True)
    redis_mock.delete = AsyncMock(return_value=1)
    redis_mock.sadd = AsyncMock(return_value=1)
    redis_mock.srem = AsyncMock(return_value=1)
    redis_mock.expire = AsyncMock(return_value=True)
    redis_mock.smembers = AsyncMock(return_value=set())
    redis_mock.aclose = AsyncMock()
    return redis_mock


@pytest.mark.asyncio
async def test_store_refresh_token(token_manager, mock_redis):
    """Test storing refresh token in Redis"""
    # Line 30-50: Test refresh token storage
    # Reason: Verify tokens are stored correctly in Redis
    # Solution: Mock Redis and verify setex is called with correct parameters
    
    token_manager.redis_client = mock_redis
    
    result = await token_manager.store_refresh_token(
        user_id="user123",
        refresh_token="refresh_token_abc",
        expires_in_seconds=604800
    )
    
    assert result is True
    mock_redis.setex.assert_called_once()
    mock_redis.sadd.assert_called()


@pytest.mark.asyncio
async def test_store_refresh_token_with_rotation(token_manager, mock_redis):
    """Test storing refresh token with rotation"""
    # Line 52-70: Test token rotation
    # Reason: Verify old token is invalidated when new one is stored
    # Solution: Mock Redis and verify old token is deleted
    
    token_manager.redis_client = mock_redis
    
    result = await token_manager.store_refresh_token(
        user_id="user123",
        refresh_token="new_refresh_token",
        expires_in_seconds=604800,
        old_token="old_refresh_token"
    )
    
    assert result is True
    mock_redis.delete.assert_called()
    mock_redis.setex.assert_called_once()


@pytest.mark.asyncio
async def test_validate_refresh_token_valid(token_manager, mock_redis):
    """Test validating a valid refresh token"""
    # Line 72-90: Test token validation with valid token
    # Reason: Verify valid tokens are correctly identified
    # Solution: Mock Redis to return token data
    
    import json
    token_data = {"user_id": "user123", "created_at": "2025-01-01T00:00:00", "token_family": "family1"}
    mock_redis.get = AsyncMock(return_value=json.dumps(token_data))
    token_manager.redis_client = mock_redis
    
    result = await token_manager.validate_refresh_token("refresh_token_abc")
    
    assert result is not None
    assert result["user_id"] == "user123"


@pytest.mark.asyncio
async def test_validate_refresh_token_invalid(token_manager, mock_redis):
    """Test validating an invalid refresh token"""
    # Line 92-105: Test token validation with invalid token
    # Reason: Verify invalid tokens return None
    # Solution: Mock Redis to return None
    
    mock_redis.get = AsyncMock(return_value=None)
    token_manager.redis_client = mock_redis
    
    result = await token_manager.validate_refresh_token("invalid_token")
    
    assert result is None


@pytest.mark.asyncio
async def test_revoke_refresh_token(token_manager, mock_redis):
    """Test revoking a refresh token"""
    # Line 107-130: Test token revocation
    # Reason: Verify tokens can be revoked
    # Solution: Mock Redis and verify token is deleted
    
    import json
    token_data = {"user_id": "user123"}
    mock_redis.get = AsyncMock(return_value=json.dumps(token_data))
    token_manager.redis_client = mock_redis
    
    result = await token_manager.revoke_refresh_token("refresh_token_abc")
    
    assert result is True
    mock_redis.delete.assert_called()
    mock_redis.srem.assert_called()


@pytest.mark.asyncio
async def test_revoke_all_user_tokens(token_manager, mock_redis):
    """Test revoking all tokens for a user"""
    # Line 132-150: Test bulk token revocation
    # Reason: Verify all user tokens can be revoked
    # Solution: Mock Redis and verify all tokens are deleted
    
    mock_redis.smembers = AsyncMock(return_value={"token1", "token2"})
    token_manager.redis_client = mock_redis
    
    result = await token_manager.revoke_all_user_tokens("user123")
    
    assert result is True
    assert mock_redis.delete.call_count >= 1


@pytest.mark.asyncio
async def test_connect_redis(token_manager):
    """Test Redis connection"""
    # Line 152-165: Test Redis connection
    # Reason: Verify Redis connection is established
    # Solution: Mock aioredis.from_url
    
    with patch("app.utils.token_manager.aioredis.from_url", new_callable=AsyncMock) as mock_from_url:
        mock_redis = AsyncMock()
        mock_from_url.return_value = mock_redis
        
        await token_manager.connect_redis()
        
        assert token_manager.redis_client is not None
        mock_from_url.assert_called_once()


@pytest.mark.asyncio
async def test_close_redis(token_manager, mock_redis):
    """Test closing Redis connection"""
    # Line 167-175: Test Redis connection closure
    # Reason: Verify Redis connection is properly closed
    # Solution: Mock Redis and verify aclose is called
    
    token_manager.redis_client = mock_redis
    
    await token_manager.close_redis()
    
    assert token_manager.redis_client is None
    mock_redis.aclose.assert_called_once()

