"""
Authentication router for token refresh and revocation

This module provides endpoints for:
- /auth/refresh - Refresh access token using refresh token
- /auth/revoke - Revoke refresh token
"""

from typing import Optional
from fastapi import APIRouter, Request, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from app.settings import get_settings
from app.utils.token_manager import TokenManager
from app.utils.audit_logger import AuditLogger
from app.middleware.auth import AuthMiddleware
from app.core.discovery import create_service_discovery
import httpx
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])

# Initialize utilities
token_manager = TokenManager()
audit_logger = AuditLogger()
settings = get_settings()


class RefreshTokenRequest(BaseModel):
    """Request model for token refresh"""
    refresh_token: str = Field(..., description="Refresh token")


class RefreshTokenResponse(BaseModel):
    """Response model for token refresh"""
    access_token: str = Field(..., description="New access token")
    refresh_token: str = Field(..., description="New refresh token (if rotation enabled)")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration in seconds")


class RevokeTokenRequest(BaseModel):
    """Request model for token revocation"""
    refresh_token: str = Field(..., description="Refresh token to revoke")


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    request: Request,
    body: RefreshTokenRequest
) -> RefreshTokenResponse:
    """
    Refresh access token using refresh token
    
    This endpoint:
    1. Validates the refresh token from Redis
    2. Calls auth-service to generate new tokens
    3. Implements refresh token rotation (if enabled)
    4. Stores new refresh token in Redis
    5. Logs the refresh event for audit
    
    Args:
        request: FastAPI request object
        body: Refresh token request
        
    Returns:
        New access token and refresh token
        
    Raises:
        HTTPException: If refresh token is invalid or expired
    """
    # Line 60-150: Token refresh endpoint with rotation support
    # Reason: Allow clients to refresh expired access tokens
    #         Implement refresh token rotation for enhanced security
    # Solution: Validate refresh token, call auth-service, rotate if enabled
    
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    try:
        # Validate refresh token from Redis
        token_data = await token_manager.validate_refresh_token(body.refresh_token)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        user_id = token_data.get("user_id")
        old_token_family = token_data.get("token_family")
        
        # Get auth-service instance
        service_discovery = create_service_discovery()
        instances = await service_discovery.get_instances("auth-service")
        if not instances:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Auth service not available"
            )
        
        # Call auth-service to refresh token
        # Auth-service will generate new access_token and refresh_token
        auth_service_url = instances[0].url
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{auth_service_url}/auth/refresh",
                json={"refresh_token": body.refresh_token},
                headers={
                    "Content-Type": "application/json",
                    "X-User-Id": user_id
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.text or "Failed to refresh token"
                )
            
            token_response = response.json()
            new_access_token = token_response.get("access_token")
            new_refresh_token = token_response.get("refresh_token")
            expires_in = token_response.get("expires_in", settings.jwt_expiration_minutes * 60)
        
        # Store new refresh token in Redis with rotation
        refresh_expires_in = settings.jwt_refresh_expiration_days * 24 * 60 * 60
        
        if settings.jwt_refresh_rotation_enabled and new_refresh_token:
            # Token rotation: invalidate old token, store new one
            await token_manager.store_refresh_token(
                user_id=user_id,
                refresh_token=new_refresh_token,
                expires_in_seconds=refresh_expires_in,
                token_family=old_token_family,
                old_token=body.refresh_token
            )
        elif new_refresh_token:
            # No rotation: just store new token (old one remains valid until expiry)
            await token_manager.store_refresh_token(
                user_id=user_id,
                refresh_token=new_refresh_token,
                expires_in_seconds=refresh_expires_in,
                token_family=old_token_family
            )
        
        # Log refresh event for audit
        await audit_logger.log_refresh(
            user_id=user_id,
            ip_address=client_ip,
            user_agent=user_agent,
            details={
                "token_rotation": settings.jwt_refresh_rotation_enabled,
                "old_token_family": old_token_family
            }
        )
        
        return RefreshTokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token or body.refresh_token,
            token_type="Bearer",
            expires_in=expires_in
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing token: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/revoke")
async def revoke_token(
    request: Request,
    body: RevokeTokenRequest
) -> JSONResponse:
    """
    Revoke refresh token
    
    This endpoint:
    1. Validates the refresh token
    2. Revokes it from Redis
    3. Logs the revocation event for audit
    
    Args:
        request: FastAPI request object
        body: Revoke token request
        
    Returns:
        Success response
        
    Raises:
        HTTPException: If token revocation fails
    """
    # Line 152-200: Token revocation endpoint
    # Reason: Allow users to logout and invalidate refresh tokens
    # Solution: Remove token from Redis and log audit event
    
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    try:
        # Validate token to get user_id
        token_data = await token_manager.validate_refresh_token(body.refresh_token)
        if not token_data:
            # Token already invalid or expired
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"message": "Token revoked or already invalid"}
            )
        
        user_id = token_data.get("user_id")
        
        # Revoke token
        success = await token_manager.revoke_refresh_token(body.refresh_token)
        
        if success:
            # Log revocation event for audit
            await audit_logger.log_revoke(
                user_id=user_id,
                ip_address=client_ip,
                user_agent=user_agent,
                details={"token": body.refresh_token[:20] + "..."}
            )
            
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"message": "Token revoked successfully"}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to revoke token"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error revoking token: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

