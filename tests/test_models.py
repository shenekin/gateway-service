"""
Unit tests for data models
"""

import pytest
from app.models.context import RequestContext, UserContext
from app.models.route import Route, RouteConfig


def test_user_context():
    """Test UserContext model"""
    user = UserContext(
        user_id="123",
        username="test_user",
        email="test@example.com",
        tenant_id="tenant_a",
        roles=["admin", "user"],
        is_active=True
    )
    
    assert user.user_id == "123"
    assert user.username == "test_user"
    assert len(user.roles) == 2


def test_request_context():
    """Test RequestContext model"""
    context = RequestContext(
        method="GET",
        path="/projects/123"
    )
    
    assert context.method == "GET"
    assert context.path == "/projects/123"
    assert context.request_id is not None
    assert context.trace_id is not None


def test_request_context_forward_headers():
    """Test RequestContext forward headers generation"""
    user = UserContext(
        user_id="123",
        tenant_id="tenant_a",
        roles=["admin"],
        is_active=True
    )
    
    context = RequestContext(
        method="GET",
        path="/projects",
        user_context=user
    )
    
    headers = context.to_forward_headers()
    
    assert "X-Request-Id" in headers
    assert "X-Trace-Id" in headers
    assert headers["X-User-Id"] == "123"
    assert headers["X-Tenant-Id"] == "tenant_a"
    assert headers["X-Roles"] == "admin"
    assert headers["X-Active"] == "true"


def test_route_config():
    """Test RouteConfig model"""
    config = RouteConfig(
        path="/projects",
        service="project-service",
        methods=["GET", "POST"],
        auth_required=True,
        rate_limit=100
    )
    
    assert config.path == "/projects"
    assert config.service == "project-service"
    assert "GET" in config.methods
    assert config.auth_required is True

