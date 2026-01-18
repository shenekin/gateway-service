"""
Unit tests to verify RBAC functionality has been removed
Tests ensure that RBAC is not imported or used anywhere
"""

import pytest
import sys
from importlib import import_module


class TestRBACRemoval:
    """Test cases to verify RBAC removal"""
    
    def test_rbac_module_not_importable(self):
        """
        Test that RBAC module cannot be imported
        
        This test verifies that app.middleware.rbac module has been removed
        """
        with pytest.raises(ModuleNotFoundError, match="No module named 'app.middleware.rbac'"):
            from app.middleware.rbac import RBACMiddleware
    
    def test_rbac_not_in_middleware_init(self):
        """Test that RBACMiddleware is not exported from middleware __init__"""
        from app.middleware import __all__
        
        assert "RBACMiddleware" not in __all__
    
    def test_bootstrap_no_rbac_import(self):
        """Test that bootstrap.py does not import RBAC"""
        import inspect
        from app import bootstrap
        
        source = inspect.getsource(bootstrap)
        assert "RBACMiddleware" not in source
        assert "from app.middleware.rbac" not in source
    
    def test_main_no_rbac_import(self):
        """Test that main.py does not import RBAC"""
        import inspect
        from app import main
        
        source = inspect.getsource(main)
        assert "RBACMiddleware" not in source
        assert "from app.middleware.rbac" not in source
        assert "rbac_middleware" not in source
    
    def test_middleware_init_no_rbac(self):
        """Test that middleware __init__.py does not import RBAC"""
        import inspect
        from app.middleware import __init__ as middleware_init
        
        source = inspect.getsource(middleware_init)
        assert "RBACMiddleware" not in source
        assert "from app.middleware.rbac" not in source
    
    def test_app_can_start_without_rbac(self):
        """Test that application can be created without RBAC"""
        from app.bootstrap import create_app
        
        # Should not raise any import errors
        app = create_app()
        assert app is not None
    
    def test_auth_middleware_still_works(self):
        """Test that authentication middleware still works after RBAC removal"""
        from app.middleware.auth import AuthMiddleware
        
        middleware = AuthMiddleware()
        assert middleware is not None
        assert hasattr(middleware, 'authenticate_jwt')
        assert hasattr(middleware, 'authenticate_api_key')
    
    def test_rate_limit_middleware_still_works(self):
        """Test that rate limit middleware still works after RBAC removal"""
        from app.middleware.rate_limit import RateLimitMiddleware
        
        middleware = RateLimitMiddleware()
        assert middleware is not None
        assert hasattr(middleware, 'check_rate_limit')
    
    def test_no_rbac_files_exist(self):
        """Test that RBAC files have been deleted"""
        from pathlib import Path
        
        rbac_file = Path(__file__).parent.parent / "app" / "middleware" / "rbac.py"
        rbac_test_file = Path(__file__).parent / "test_rbac.py"
        
        assert not rbac_file.exists(), "RBAC middleware file should not exist"
        assert not rbac_test_file.exists(), "RBAC test file should not exist"
    
    def test_route_auth_required_still_works(self):
        """Test that route-level auth_required flag still works"""
        from app.models.route import Route, RouteConfig
        
        # Test route with auth required
        route_with_auth = Route(
            config=RouteConfig(
                path="/protected",
                service="test-service",
                auth_required=True
            ),
            pattern="/protected"
        )
        
        # Test route without auth required
        route_without_auth = Route(
            config=RouteConfig(
                path="/public",
                service="test-service",
                auth_required=False
            ),
            pattern="/public"
        )
        
        assert route_with_auth.config.auth_required is True
        assert route_without_auth.config.auth_required is False

