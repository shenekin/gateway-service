"""
Authentication middleware for JWT and API key validation
"""

# Line 5: Import jwt from PyJWT package
# Reason: Bug fix for ModuleNotFoundError: No module named 'jwt'
# Root Cause:
#   - Code uses PyJWT API (jwt.decode(), jwt.ExpiredSignatureError, jwt.InvalidTokenError)
#   - requirements.txt only had python-jose which has different API
#   - PyJWT package was missing from requirements.txt
# Solution:
#   - Added PyJWT==2.8.0 to requirements.txt
#   - Import statement 'import jwt' is correct for PyJWT package
#   - PyJWT provides the jwt module that this code expects
import jwt
from typing import Optional, Callable
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.context import UserContext
from app.settings import get_settings
from app.utils.crypto import CryptoUtils


class AuthMiddleware:
    """Authentication middleware for JWT and API key"""
    
    def __init__(self):
        """Initialize authentication middleware"""
        self.settings = get_settings()
        self.security = HTTPBearer(auto_error=False)
        self.crypto_utils = CryptoUtils()
        self._load_keys()
    
    def _load_keys(self) -> None:
        """Load JWT keys if configured"""
        self.public_key = None
        self.private_key = None
        
        if self.settings.jwt_public_key_path:
            self.public_key = CryptoUtils.load_public_key(self.settings.jwt_public_key_path)
        
        if self.settings.jwt_private_key_path:
            self.private_key = CryptoUtils.load_private_key(self.settings.jwt_private_key_path)
    
    async def authenticate_jwt(self, request: Request) -> Optional[UserContext]:
        """
        Authenticate request using JWT token
        
        Args:
            request: FastAPI request object
            
        Returns:
            User context if authenticated, None otherwise
            
        Raises:
            HTTPException: If authentication fails
        """
        credentials: Optional[HTTPAuthorizationCredentials] = await self.security(request)
        
        if not credentials:
            return None
        
        token = credentials.credentials
        
        try:
            if self.settings.jwt_algorithm.startswith("RS"):
                if not self.public_key:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="JWT public key not configured"
                    )
                payload = jwt.decode(
                    token,
                    self.public_key,
                    algorithms=[self.settings.jwt_algorithm]
                )
            else:
                payload = jwt.decode(
                    token,
                    self.settings.jwt_secret_key,
                    algorithms=[self.settings.jwt_algorithm]
                )
            
            # Extract user information from payload
            user_id = payload.get("sub") or payload.get("user_id")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing user identifier"
                )
            
            return UserContext(
                user_id=str(user_id),
                username=payload.get("username"),
                email=payload.get("email"),
                tenant_id=payload.get("tenant_id"),
                roles=payload.get("roles", []),
                permissions=payload.get("permissions", []),
                is_active=payload.get("is_active", True)
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
    
    async def authenticate_api_key(self, request: Request) -> Optional[UserContext]:
        """
        Authenticate request using API key
        
        Args:
            request: FastAPI request object
            
        Returns:
            User context if authenticated, None otherwise
            
        Raises:
            HTTPException: If authentication fails
        """
        if not self.settings.api_key_enabled:
            return None
        
        api_key = request.headers.get(self.settings.api_key_header)
        if not api_key:
            return None
        
        # In production, this would query database
        # For now, return a placeholder implementation
        # user = await self._get_user_by_api_key(api_key)
        # if not user:
        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED,
        #         detail="Invalid API key"
        #     )
        # return UserContext(...)
        
        return None
    
    async def authenticate(self, request: Request) -> Optional[UserContext]:
        """
        Authenticate request using JWT or API key
        
        Args:
            request: FastAPI request object
            
        Returns:
            User context if authenticated, None otherwise
        """
        # Try JWT first
        user_context = await self.authenticate_jwt(request)
        if user_context:
            return user_context
        
        # Try API key
        user_context = await self.authenticate_api_key(request)
        if user_context:
            return user_context
        
        return None
    
    async def __call__(self, request: Request, call_next: Callable) -> any:
        """
        Middleware execution
        
        Args:
            request: FastAPI request object
            call_next: Next middleware or route handler
            
        Returns:
            Response
        """
        # Authentication is handled per-route based on route config
        # This middleware just makes auth available
        response = await call_next(request)
        return response

