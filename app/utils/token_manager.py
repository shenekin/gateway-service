"""
Token management utility for refresh token storage and rotation

This module provides functionality for managing refresh tokens in Redis
and implementing refresh token rotation for enhanced security.
"""

import uuid
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import redis.asyncio as aioredis
from app.settings import get_settings


class TokenManager:
    """
    Manages refresh tokens in Redis with rotation support
    
    This class handles:
    - Storing refresh tokens in Redis
    - Token rotation (old token invalidated when new one is issued)
    - Token revocation
    - Token validation
    """
    
    def __init__(self):
        """Initialize token manager"""
        self.settings = get_settings()
        self.redis_client: Optional[aioredis.Redis] = None
        self._token_prefix = "refresh_token:"
        self._family_prefix = "token_family:"
    
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
    
    async def store_refresh_token(
        self,
        user_id: str,
        refresh_token: str,
        expires_in_seconds: int,
        token_family: Optional[str] = None,
        old_token: Optional[str] = None
    ) -> bool:
        """
        Store refresh token in Redis
        
        If old_token is provided, implements token rotation by invalidating
        the old token before storing the new one.
        
        Args:
            user_id: User identifier
            refresh_token: Refresh token string
            expires_in_seconds: Token expiration time in seconds
            token_family: Optional token family ID for rotation tracking
            old_token: Optional old token to invalidate (rotation)
            
        Returns:
            True if successful, False otherwise
        """
        # Line 60-95: Store refresh token in Redis with rotation support
        # Reason: Store refresh tokens securely in Redis for validation and rotation
        #         Token rotation invalidates old token when new one is issued
        # Solution: Store token with user_id mapping and optional family tracking
        
        await self.connect_redis()
        
        try:
            # If old token provided, invalidate it first (rotation)
            if old_token:
                old_key = f"{self._token_prefix}{old_token}"
                await self.redis_client.delete(old_key)
            
            # Store new token
            token_key = f"{self._token_prefix}{refresh_token}"
            token_data = {
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "token_family": token_family or str(uuid.uuid4())
            }
            
            # Store with expiration
            await self.redis_client.setex(
                token_key,
                expires_in_seconds,
                json.dumps(token_data)
            )
            
            # Also store user_id -> token mapping for revocation
            user_tokens_key = f"user_tokens:{user_id}"
            await self.redis_client.sadd(user_tokens_key, refresh_token)
            await self.redis_client.expire(user_tokens_key, expires_in_seconds)
            
            # Track token family if provided
            if token_family:
                family_key = f"{self._family_prefix}{token_family}"
                await self.redis_client.sadd(family_key, refresh_token)
                await self.redis_client.expire(family_key, expires_in_seconds)
            
            return True
        except Exception:
            return False
    
    async def validate_refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        Validate refresh token and return token data
        
        Args:
            refresh_token: Refresh token string
            
        Returns:
            Token data dictionary if valid, None otherwise
        """
        # Line 97-120: Validate refresh token from Redis
        # Reason: Verify refresh token is valid and not revoked
        # Solution: Check Redis for token existence and return stored data
        
        await self.connect_redis()
        
        try:
            token_key = f"{self._token_prefix}{refresh_token}"
            token_data_str = await self.redis_client.get(token_key)
            
            if not token_data_str:
                return None
            
            token_data = json.loads(token_data_str)
            return token_data
        except Exception:
            return None
    
    async def revoke_refresh_token(self, refresh_token: str) -> bool:
        """
        Revoke a refresh token
        
        Args:
            refresh_token: Refresh token to revoke
            
        Returns:
            True if successful, False otherwise
        """
        # Line 122-145: Revoke refresh token
        # Reason: Allow users to logout and invalidate tokens
        # Solution: Delete token from Redis
        
        await self.connect_redis()
        
        try:
            token_key = f"{self._token_prefix}{refresh_token}"
            token_data_str = await self.redis_client.get(token_key)
            
            if token_data_str:
                token_data = json.loads(token_data_str)
                user_id = token_data.get("user_id")
                
                # Delete token
                await self.redis_client.delete(token_key)
                
                # Remove from user tokens set
                if user_id:
                    user_tokens_key = f"user_tokens:{user_id}"
                    await self.redis_client.srem(user_tokens_key, refresh_token)
                
                return True
            
            return False
        except Exception:
            return False
    
    async def revoke_all_user_tokens(self, user_id: str) -> bool:
        """
        Revoke all refresh tokens for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            True if successful, False otherwise
        """
        # Line 147-170: Revoke all user tokens
        # Reason: Allow bulk token revocation (e.g., on password change)
        # Solution: Get all user tokens and revoke each one
        
        await self.connect_redis()
        
        try:
            user_tokens_key = f"user_tokens:{user_id}"
            tokens = await self.redis_client.smembers(user_tokens_key)
            
            for token in tokens:
                await self.revoke_refresh_token(token)
            
            await self.redis_client.delete(user_tokens_key)
            return True
        except Exception:
            return False

