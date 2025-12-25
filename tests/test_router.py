"""
Unit tests for router module
"""

import pytest
from app.core.router import Router
from app.models.route import Route, RouteConfig


def test_router_initialization():
    """Test router initialization"""
    router = Router()
    assert router is not None
    assert len(router.get_all_routes()) > 0


def test_router_find_route():
    """Test route finding"""
    router = Router()
    
    # Test exact match
    route = router.find_route("/projects", "GET")
    assert route is not None
    assert route.config.service == "project-service"
    
    # Test path with parameter
    route = router.find_route("/projects/123", "GET")
    assert route is not None
    
    # Test non-existent route
    route = router.find_route("/nonexistent", "GET")
    assert route is None


def test_route_matching():
    """Test route matching logic"""
    config = RouteConfig(
        path="/projects",
        service="project-service",
        methods=["GET", "POST"]
    )
    route = Route(config=config, pattern="/projects")
    
    assert route.matches("/projects", "GET") is True
    assert route.matches("/projects", "POST") is True
    assert route.matches("/projects", "DELETE") is False
    assert route.matches("/projects/123", "GET") is False


def test_route_wildcard_matching():
    """Test wildcard route matching"""
    config = RouteConfig(
        path="/projects/**",
        service="project-service",
        methods=["GET"]
    )
    route = Route(config=config, pattern="/projects/**")
    
    assert route.matches("/projects", "GET") is True
    assert route.matches("/projects/123", "GET") is True
    assert route.matches("/projects/123/details", "GET") is True


def test_route_path_params():
    """Test path parameter extraction"""
    config = RouteConfig(
        path="/projects/{project_id}",
        service="project-service",
        methods=["GET"]
    )
    route = Route(config=config, pattern="/projects/{project_id}")
    
    params = route.extract_path_params("/projects/123")
    assert params["project_id"] == "123"

