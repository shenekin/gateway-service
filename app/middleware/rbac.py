"""
Role-Based Access Control (RBAC) middleware
"""

from typing import Optional, Callable, List
from fastapi import Request, HTTPException, status
from app.models.context import UserContext, RequestContext
from app.models.route import Route


class RBACMiddleware:
    """RBAC middleware for authorization"""
    
    def __init__(self):
        """Initialize RBAC middleware"""
        pass
    
    def check_permission(
        self,
        user_context: Optional[UserContext],
        route: Route,
        method: str
    ) -> bool:
        """
        Check if user has permission to access route
        
        Args:
            user_context: User context
            route: Route configuration
            method: HTTP method
            
        Returns:
            True if user has permission, False otherwise
        """
        if not route.config.auth_required:
            return True
        
        if not user_context:
            return False
        
        if not user_context.is_active:
            return False
        
        # Coarse-grained authorization at gateway level
        # Fine-grained authorization should be done at backend
        return True
    
    def check_role(
        self,
        user_context: Optional[UserContext],
        required_roles: List[str]
    ) -> bool:
        """
        Check if user has required roles
        
        Args:
            user_context: User context
            required_roles: List of required roles
            
        Returns:
            True if user has at least one required role
        """
        if not user_context:
            return False
        
        if not required_roles:
            return True
        
        user_roles = set(user_context.roles)
        required_roles_set = set(required_roles)
        
        return bool(user_roles.intersection(required_roles_set))
    
    def check_permission_string(
        self,
        user_context: Optional[UserContext],
        required_permission: str
    ) -> bool:
        """
        Check if user has required permission
        
        Args:
            user_context: User context
            required_permission: Required permission string
            
        Returns:
            True if user has permission
        """
        if not user_context:
            return False
        
        if not required_permission:
            return True
        
        user_permissions = set(user_context.permissions)
        return required_permission in user_permissions
    
    async def authorize(
        self,
        user_context: Optional[UserContext],
        route: Route,
        method: str
    ) -> None:
        """
        Authorize request
        
        Args:
            user_context: User context
            route: Route configuration
            method: HTTP method
            
        Raises:
            HTTPException: If authorization fails
        """
        if not self.check_permission(user_context, route, method):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
    
    async def __call__(self, request: Request, call_next: Callable) -> any:
        """
        Middleware execution
        
        Args:
            request: FastAPI request object
            call_next: Next middleware or route handler
            
        Returns:
            Response
        """
        # Authorization is handled per-route
        response = await call_next(request)
        return response

