"""
Unit tests for authentication router

Tests cover:
- /auth/refresh endpoint
- /auth/revoke endpoint
- Token rotation
- Audit logging integration
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.utils.token_manager import TokenManager
from app.utils.audit_logger import AuditLogger


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_token_data():
    """Mock token data"""
    return {
        "user_id": "user123",
        "created_at": "2025-01-01T00:00:00",
        "token_family": "family1"
    }


@pytest.fixture
def mock_auth_service_response():
    """Mock auth-service response"""
    return {
        "access_token": "new_access_token",
        "refresh_token": "new_refresh_token",
        "expires_in": 1800
    }


@pytest.mark.asyncio
async def test_refresh_token_success(client, mock_token_data, mock_auth_service_response):
    """Test successful token refresh"""
    # Line 30-70: Test token refresh endpoint
    # Reason: Verify refresh endpoint works correctly
    # Solution: Mock TokenManager and auth-service response
    
    with patch.object(TokenManager, "validate_refresh_token", return_value=mock_token_data), \
         patch.object(TokenManager, "store_refresh_token", return_value=True), \
         patch("app.routers.auth.create_service_discovery") as mock_discovery, \
         patch("httpx.AsyncClient") as mock_client:
        
        # Mock service discovery
        mock_instance = MagicMock()
        mock_instance.url = "http://auth-service:8000"
        mock_discovery.return_value.get_instances = AsyncMock(return_value=[mock_instance])
        
        # Mock HTTP client
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_auth_service_response
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        
        # Mock audit logger
        with patch.object(AuditLogger, "log_refresh", return_value=None):
            response = client.post(
                "/auth/refresh",
                json={"refresh_token": "old_refresh_token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data


@pytest.mark.asyncio
async def test_refresh_token_invalid(client):
    """Test refresh with invalid token"""
    # Line 72-90: Test refresh with invalid token
    # Reason: Verify invalid tokens are rejected
    # Solution: Mock TokenManager to return None
    
    with patch.object(TokenManager, "validate_refresh_token", return_value=None):
        response = client.post(
            "/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )
        
        assert response.status_code == 401
        assert "Invalid or expired" in response.json()["detail"]


@pytest.mark.asyncio
async def test_refresh_token_with_rotation(client, mock_token_data, mock_auth_service_response):
    """Test token refresh with rotation enabled"""
    # Line 92-120: Test token rotation
    # Reason: Verify old token is invalidated when rotation is enabled
    # Solution: Mock TokenManager and verify old token is passed
    
    with patch.object(TokenManager, "validate_refresh_token", return_value=mock_token_data), \
         patch.object(TokenManager, "store_refresh_token", return_value=True) as mock_store, \
         patch("app.routers.auth.create_service_discovery") as mock_discovery, \
         patch("httpx.AsyncClient") as mock_client:
        
        # Mock service discovery
        mock_instance = MagicMock()
        mock_instance.url = "http://auth-service:8000"
        mock_discovery.return_value.get_instances = AsyncMock(return_value=[mock_instance])
        
        # Mock HTTP client
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_auth_service_response
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        
        # Mock audit logger
        with patch.object(AuditLogger, "log_refresh", return_value=None):
            response = client.post(
                "/auth/refresh",
                json={"refresh_token": "old_refresh_token"}
            )
            
            assert response.status_code == 200
            # Verify store_refresh_token was called with old_token for rotation
            mock_store.assert_called()
            call_args = mock_store.call_args
            assert "old_token" in call_args.kwargs or "old_token" in str(call_args)


@pytest.mark.asyncio
async def test_revoke_token_success(client, mock_token_data):
    """Test successful token revocation"""
    # Line 122-150: Test token revocation endpoint
    # Reason: Verify tokens can be revoked
    # Solution: Mock TokenManager and verify revoke is called
    
    with patch.object(TokenManager, "validate_refresh_token", return_value=mock_token_data), \
         patch.object(TokenManager, "revoke_refresh_token", return_value=True), \
         patch.object(AuditLogger, "log_revoke", return_value=None):
        
        response = client.post(
            "/auth/revoke",
            json={"refresh_token": "refresh_token_abc"}
        )
        
        assert response.status_code == 200
        assert "revoked" in response.json()["message"].lower()


@pytest.mark.asyncio
async def test_revoke_token_already_invalid(client):
    """Test revoking already invalid token"""
    # Line 152-170: Test revoking invalid token
    # Reason: Verify revoking invalid token doesn't error
    # Solution: Mock TokenManager to return None
    
    with patch.object(TokenManager, "validate_refresh_token", return_value=None):
        response = client.post(
            "/auth/revoke",
            json={"refresh_token": "invalid_token"}
        )
        
        # Should return 200 even if token is already invalid
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_refresh_token_auth_service_unavailable(client, mock_token_data):
    """Test refresh when auth-service is unavailable"""
    # Line 172-190: Test error handling when auth-service is down
    # Reason: Verify proper error when auth-service is unavailable
    # Solution: Mock service discovery to return empty list
    
    with patch.object(TokenManager, "validate_refresh_token", return_value=mock_token_data), \
         patch("app.routers.auth.create_service_discovery") as mock_discovery:
        
        mock_discovery.return_value.get_instances = AsyncMock(return_value=[])
        
        response = client.post(
            "/auth/refresh",
            json={"refresh_token": "refresh_token_abc"}
        )
        
        assert response.status_code == 503
        assert "not available" in response.json()["detail"]

