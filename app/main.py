"""
Main application entry point
"""

import uuid
from typing import Optional
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from app.bootstrap import create_app
from app.models.context import RequestContext, UserContext
from app.middleware.auth import AuthMiddleware
# Line 12: Removed RBACMiddleware import
# Reason: RBAC functionality removed as per requirements - not being developed at this stage
# RBAC middleware and related tests have been removed from the project
from app.middleware.rate_limit import RateLimitMiddleware

# Create application
app = create_app()

# Initialize middleware
auth_middleware = AuthMiddleware()
# Line 20: Removed RBACMiddleware initialization
# Reason: RBAC functionality removed as per requirements - not being developed at this stage
rate_limit_middleware = RateLimitMiddleware()


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    """
    Create request context and attach to request state
    
    Args:
        request: FastAPI request object
        call_next: Next middleware or route handler
        
    Returns:
        Response
    """
    # Create request context
    context = RequestContext(
        request_id=str(uuid.uuid4()),
        trace_id=request.headers.get("X-Trace-Id", str(uuid.uuid4())),
        method=request.method,
        path=request.url.path,
        query_params=dict(request.query_params),
        headers=dict(request.headers),
        client_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    # Store in request state
    request.state.request_id = context.request_id
    request.state.trace_id = context.trace_id
    request.state.context = context
    
    response = await call_next(request)
    
    # Add trace headers to response
    response.headers["X-Request-Id"] = context.request_id
    response.headers["X-Trace-Id"] = context.trace_id
    
    return response


@app.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": "gateway-service"
    }


@app.get("/ready")
async def readiness_check(request: Request) -> dict:
    """
    Readiness check endpoint
    
    Args:
        request: FastAPI request object
        
    Returns:
        Readiness status
    """
    # Check if services are ready
    try:
        # Check service discovery
        service_discovery = request.app.state.service_discovery
        instances = await service_discovery.get_instances("project-service")
        
        return {
            "status": "ready",
            "service": "gateway-service",
            "services_available": len(instances) > 0
        }
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "error": str(e)
            }
        )


@app.get("/metrics")
async def metrics() -> dict:
    """
    Prometheus metrics endpoint
    
    Returns:
        Metrics data
    """
    # In production, this would export Prometheus metrics
    return {
        "requests_total": 0,
        "requests_per_second": 0
    }


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def gateway_handler(request: Request, path: str) -> Response:
    """
    Main gateway handler for routing requests to backend services
    
    Args:
        request: FastAPI request object
        path: Request path
        
    Returns:
        Response from backend service
    """
    context: RequestContext = request.state.context
    router = request.app.state.router
    service_discovery = request.app.state.service_discovery
    proxy_service = request.app.state.proxy_service
    
    # Find matching route
    route = router.find_route(f"/{path}", request.method)
    if not route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Route not found: {request.method} /{path}"
        )
    
    context.service_name = route.config.service
    context.route_config = route.config.dict()
    
    # Extract path parameters
    context.path_params = route.extract_path_params(f"/{path}")
    
    # Handle internal routes
    if route.config.service == "internal":
        if path == "health":
            return await health_check()
        elif path == "ready":
            return await readiness_check(request)
        elif path == "metrics":
            return await metrics()
    
    # Authentication
    user_context: Optional[UserContext] = None
    if route.config.auth_required:
        user_context = await auth_middleware.authenticate(request)
        if not user_context:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        context.user_context = user_context
        request.state.user_id = user_context.user_id
        request.state.tenant_id = user_context.tenant_id
    
    # Authorization
    # Line 177: Removed RBAC authorization call
    # Reason: RBAC functionality removed as per requirements - not being developed at this stage
    # Basic authorization is handled by checking auth_required flag in route config
    # Fine-grained authorization should be handled by backend services
    
    # Rate limiting
    is_allowed, remaining = await rate_limit_middleware.check_request_rate_limit(
        request,
        route_path=route.config.path,
        custom_limit=route.config.rate_limit
    )
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
    request.state.rate_limit_remaining = remaining
    
    # Get service instances
    instances = await service_discovery.get_instances(route.config.service)
    if not instances:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Service {route.config.service} not available"
        )
    
    # Load balancing
    from app.core.load_balancer import LoadBalancer
    load_balancer = LoadBalancer()
    selected_instance = load_balancer.select_instance(instances, route.config.service)
    if not selected_instance:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No healthy service instances available"
        )
    
    # Prepare request path
    forward_path = f"/{path}"
    if route.config.strip_prefix:
        # Remove route prefix from path
        prefix = route.config.path.rstrip("/**").rstrip("/*")
        if forward_path.startswith(prefix):
            forward_path = forward_path[len(prefix):]
    
    if route.config.rewrite_path:
        forward_path = route.config.rewrite_path
    
    # Get request body
    body = await request.body()
    
    # Forward request
    try:
        response = await proxy_service.forward_request(
            instance=selected_instance,
            context=context,
            method=request.method,
            path=forward_path,
            headers=route.config.headers,
            query_params=context.query_params,
            body=body if body else None,
            timeout=route.config.timeout
        )
        
        # Create response
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to forward request: {str(e)}"
        )


if __name__ == "__main__":
    """
    Direct execution of main.py is deprecated.
    Please use 'python run.py' instead for the unified entry point.
    """
    import uvicorn
    from app.settings import get_settings
    
    print("Warning: Direct execution of app.main is deprecated.")
    print("Please use 'python run.py' instead for the unified entry point.")
    
    settings = get_settings()
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )

