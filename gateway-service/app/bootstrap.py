"""
Application bootstrap and initialization
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.settings import get_settings
from app.middleware.auth import AuthMiddleware
# Line 9: Removed RBACMiddleware import
# Reason: RBAC functionality removed as per requirements - not being developed at this stage
# RBAC middleware and related tests have been removed from the project
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.logging import LoggingMiddleware
from app.middleware.tracing import TracingMiddleware
from app.core.router import Router
from app.core.discovery import create_service_discovery
from app.core.proxy import ProxyService


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application
    
    Returns:
        Configured FastAPI application
    """
    settings = get_settings()
    
    app = FastAPI(
        title="Gateway Service",
        description="API Gateway for Cloud Resource Management System",
        version="1.0.0",
        debug=settings.debug
    )
    
    # Configure CORS
    if settings.cors_enabled:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.allowed_origins_list,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        )
    
    # Add middleware
    app.add_middleware(TracingMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(AuthMiddleware)
    # Line 48: Removed RBACMiddleware from middleware stack
    # Reason: RBAC functionality removed as per requirements - not being developed at this stage
    app.add_middleware(RateLimitMiddleware)
    
    # Initialize services
    router = Router()
    service_discovery = create_service_discovery()
    proxy_service = ProxyService()
    
    # Store in app state
    app.state.router = router
    app.state.service_discovery = service_discovery
    app.state.proxy_service = proxy_service
    
    # Startup event
    @app.on_event("startup")
    async def startup_event():
        """Initialize services on startup"""
        await app.state.proxy_service.start()
        await app.state.service_discovery.get_instances("project-service")  # Warm up
    
    # Shutdown event
    @app.on_event("shutdown")
    async def shutdown_event():
        """Cleanup on shutdown"""
        await app.state.proxy_service.close()
        # Create instance for cleanup (app parameter required)
        rate_limit_middleware = RateLimitMiddleware(app)
        await rate_limit_middleware.close_redis()
    
    return app

