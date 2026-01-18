"""
Route configuration models
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class RouteConfig(BaseModel):
    """Route configuration model"""
    
    path: str = Field(..., description="Route path pattern")
    service: str = Field(..., description="Target service name")
    methods: List[str] = Field(default=["GET"], description="Allowed HTTP methods")
    auth_required: bool = Field(default=True, description="Whether authentication is required")
    rate_limit: int = Field(default=100, description="Rate limit per minute")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    strip_prefix: bool = Field(default=False, description="Strip path prefix when forwarding")
    rewrite_path: Optional[str] = Field(default=None, description="Path rewrite pattern")
    headers: Dict[str, str] = Field(default_factory=dict, description="Additional headers to add")
    
    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "path": "/projects",
                "service": "project-service",
                "methods": ["GET", "POST"],
                "auth_required": True,
                "rate_limit": 100,
                "timeout": 30
            }
        }


class Route(BaseModel):
    """Route model with matching logic"""
    
    config: RouteConfig
    pattern: str = Field(..., description="Compiled route pattern")
    priority: int = Field(default=0, description="Route priority for matching")
    
    def matches(self, path: str, method: str) -> bool:
        """
        Check if route matches the given path and method
        
        Args:
            path: Request path
            method: HTTP method
            
        Returns:
            True if route matches, False otherwise
        """
        if method not in self.config.methods:
            return False
        
        # Simple prefix matching (can be extended to regex)
        if self.config.path.endswith("/**"):
            prefix = self.config.path[:-3]
            return path.startswith(prefix)
        elif self.config.path.endswith("/*"):
            prefix = self.config.path[:-2]
            return path.startswith(prefix)
        else:
            return path == self.config.path or path.startswith(self.config.path + "/")
    
    def extract_path_params(self, path: str) -> Dict[str, str]:
        """
        Extract path parameters from request path
        
        Args:
            path: Request path
            
        Returns:
            Dictionary of path parameters
        """
        params = {}
        route_parts = self.config.path.split("/")
        path_parts = path.split("/")
        
        for route_part, path_part in zip(route_parts, path_parts):
            if route_part.startswith("{") and route_part.endswith("}"):
                param_name = route_part[1:-1]
                params[param_name] = path_part
        
        return params

