"""
Unit tests for RBAC middleware
"""

import pytest
from app.middleware.rbac import RBACMiddleware
from app.models.context import UserContext
from app.models.route import Route, RouteConfig


def test_check_permission_no_auth_required():
    """Test permission check when auth not required"""
    middleware = RBACMiddleware()
    route = Route(
        config=RouteConfig(
            path="/public",
            service="public-service",
            auth_required=False
        ),
        pattern="/public"
    )
    
    result = middleware.check_permission(None, route, "GET")
    assert result is True


def test_check_permission_auth_required_no_user():
    """Test permission check when auth required but no user"""
    middleware = RBACMiddleware()
    route = Route(
        config=RouteConfig(
            path="/protected",
            service="protected-service",
            auth_required=True
        ),
        pattern="/protected"
    )
    
    result = middleware.check_permission(None, route, "GET")
    assert result is False


def test_check_permission_inactive_user():
    """Test permission check with inactive user"""
    middleware = RBACMiddleware()
    user = UserContext(user_id="123", is_active=False)
    route = Route(
        config=RouteConfig(
            path="/protected",
            service="protected-service",
            auth_required=True
        ),
        pattern="/protected"
    )
    
    result = middleware.check_permission(user, route, "GET")
    assert result is False


def test_check_role():
    """Test role checking"""
    middleware = RBACMiddleware()
    user = UserContext(user_id="123", roles=["admin", "user"])
    
    assert middleware.check_role(user, ["admin"]) is True
    assert middleware.check_role(user, ["guest"]) is False
    assert middleware.check_role(user, []) is True

