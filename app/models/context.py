"""
Request context models
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class UserContext(BaseModel):
    """User context information"""
    
    user_id: str = Field(..., description="User identifier")
    username: Optional[str] = Field(default=None, description="Username")
    email: Optional[str] = Field(default=None, description="User email")
    tenant_id: Optional[str] = Field(default=None, description="Tenant identifier")
    roles: List[str] = Field(default_factory=list, description="User roles")
    permissions: List[str] = Field(default_factory=list, description="User permissions")
    is_active: bool = Field(default=True, description="Whether user is active")
    
    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "user_id": "42",
                "username": "john_doe",
                "email": "john@example.com",
                "tenant_id": "tenant_a",
                "roles": ["user", "admin"],
                "permissions": ["read:projects", "write:projects"],
                "is_active": True
            }
        }


class RequestContext(BaseModel):
    """Request context for tracking and forwarding"""
    
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique request identifier")
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Distributed trace identifier")
    span_id: Optional[str] = Field(default=None, description="Span identifier for tracing")
    user_context: Optional[UserContext] = Field(default=None, description="User context")
    start_time: datetime = Field(default_factory=datetime.utcnow, description="Request start time")
    method: str = Field(..., description="HTTP method")
    path: str = Field(..., description="Request path")
    query_params: Dict[str, Any] = Field(default_factory=dict, description="Query parameters")
    path_params: Dict[str, str] = Field(default_factory=dict, description="Path parameters")
    headers: Dict[str, str] = Field(default_factory=dict, description="Request headers")
    client_ip: Optional[str] = Field(default=None, description="Client IP address")
    user_agent: Optional[str] = Field(default=None, description="User agent string")
    service_name: Optional[str] = Field(default=None, description="Target service name")
    route_config: Optional[Dict[str, Any]] = Field(default=None, description="Matched route configuration")
    
    def to_forward_headers(self) -> Dict[str, str]:
        """
        Convert context to headers for forwarding to backend services
        
        Returns:
            Dictionary of headers to forward
        """
        headers = {
            "X-Request-Id": self.request_id,
            "X-Trace-Id": self.trace_id,
        }
        
        if self.span_id:
            headers["X-Span-Id"] = self.span_id
        
        if self.user_context:
            headers["X-User-Id"] = self.user_context.user_id
            headers["X-Active"] = str(self.user_context.is_active).lower()
            
            if self.user_context.tenant_id:
                headers["X-Tenant-Id"] = self.user_context.tenant_id
            
            if self.user_context.roles:
                headers["X-Roles"] = ",".join(self.user_context.roles)
            
            if self.user_context.username:
                headers["X-Username"] = self.user_context.username
        
        return headers
    
    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "request_id": "abc-123",
                "trace_id": "trace-456",
                "method": "GET",
                "path": "/projects/123",
                "user_context": {
                    "user_id": "42",
                    "is_active": True
                }
            }
        }

