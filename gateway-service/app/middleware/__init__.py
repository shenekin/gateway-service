"""
Middleware modules for gateway service
"""

from app.middleware.auth import AuthMiddleware
# Line 6: Removed RBACMiddleware import
# Reason: RBAC functionality removed as per requirements - not being developed at this stage
# RBAC middleware and related tests have been removed from the project
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.logging import LoggingMiddleware
from app.middleware.tracing import TracingMiddleware

__all__ = [
    "AuthMiddleware",
    # RBACMiddleware removed - not being developed at this stage
    "RateLimitMiddleware",
    "LoggingMiddleware",
    "TracingMiddleware"
]

