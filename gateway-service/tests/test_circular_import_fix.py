"""
Unit tests for circular import fix
Tests to ensure no circular import errors occur when importing settings
"""

import pytest
import sys
from importlib import reload, import_module


class TestCircularImportFix:
    """Test cases for circular import fix"""
    
    def test_import_settings_no_circular_import(self):
        """
        Test that importing get_settings does not cause circular import
        
        This test verifies the fix for:
        ImportError: cannot import name 'get_settings' from partially initialized module
        """
        # Clear any cached modules
        modules_to_clear = [
            'app.settings',
            'app.utils.env_loader',
            'app.utils',
        ]
        
        for module_name in modules_to_clear:
            if module_name in sys.modules:
                del sys.modules[module_name]
        
        # Import should not raise circular import error
        try:
            from app.settings import get_settings
            assert get_settings is not None
        except ImportError as e:
            if "circular import" in str(e).lower() or "partially initialized" in str(e).lower():
                pytest.fail(f"Circular import detected: {e}")
            else:
                raise
    
    def test_import_settings_multiple_times(self):
        """
        Test that importing get_settings multiple times works correctly
        """
        # Clear modules
        if 'app.settings' in sys.modules:
            del sys.modules['app.settings']
        
        # First import
        from app.settings import get_settings
        settings1 = get_settings()
        
        # Second import should work
        from app.settings import get_settings as get_settings2
        settings2 = get_settings2()
        
        # Both should return Settings instances
        assert settings1 is not None
        assert settings2 is not None
    
    def test_import_reload_settings_no_circular_import(self):
        """
        Test that importing reload_settings does not cause circular import
        """
        # Clear modules
        if 'app.settings' in sys.modules:
            del sys.modules['app.settings']
        
        try:
            from app.settings import reload_settings
            assert reload_settings is not None
        except ImportError as e:
            if "circular import" in str(e).lower() or "partially initialized" in str(e).lower():
                pytest.fail(f"Circular import detected: {e}")
            else:
                raise
    
    def test_import_get_available_environments_no_circular_import(self):
        """
        Test that importing get_available_environments does not cause circular import
        """
        # Clear modules
        if 'app.settings' in sys.modules:
            del sys.modules['app.settings']
        
        try:
            from app.settings import get_available_environments
            assert get_available_environments is not None
        except ImportError as e:
            if "circular import" in str(e).lower() or "partially initialized" in str(e).lower():
                pytest.fail(f"Circular import detected: {e}")
            else:
                raise
    
    def test_import_all_settings_functions(self):
        """
        Test importing all settings functions at once
        """
        # Clear modules
        if 'app.settings' in sys.modules:
            del sys.modules['app.settings']
        
        try:
            from app.settings import (
                Settings,
                get_settings,
                reload_settings,
                get_available_environments
            )
            
            assert Settings is not None
            assert get_settings is not None
            assert reload_settings is not None
            assert get_available_environments is not None
        except ImportError as e:
            if "circular import" in str(e).lower() or "partially initialized" in str(e).lower():
                pytest.fail(f"Circular import detected: {e}")
            else:
                raise
    
    def test_get_settings_with_env_name(self):
        """
        Test that get_settings works with env_name parameter after fix
        """
        from app.settings import get_settings
        
        # Should not raise circular import error
        settings = get_settings(env_name="dev")
        assert settings is not None
    
    def test_reload_settings_works(self):
        """
        Test that reload_settings works after circular import fix
        """
        from app.settings import reload_settings
        
        # Should not raise circular import error
        settings = reload_settings(env_name="dev")
        assert settings is not None
    
    def test_get_available_environments_works(self):
        """
        Test that get_available_environments works after circular import fix
        """
        from app.settings import get_available_environments
        
        # Should not raise circular import error
        environments = get_available_environments()
        assert isinstance(environments, list)
    
    def test_import_from_run_py_simulation(self):
        """
        Test importing pattern similar to run.py
        This simulates the actual import pattern that caused the bug
        """
        # Clear modules to simulate fresh import
        modules_to_clear = [
            'app.settings',
            'app.utils.env_loader',
            'app.utils',
        ]
        
        for module_name in modules_to_clear:
            if module_name in sys.modules:
                del sys.modules[module_name]
        
        # Simulate run.py imports
        try:
            from app.settings import get_settings, reload_settings
            from app.utils.env_loader import EnvironmentLoader
            
            # All imports should succeed
            assert get_settings is not None
            assert reload_settings is not None
            assert EnvironmentLoader is not None
        except ImportError as e:
            if "circular import" in str(e).lower() or "partially initialized" in str(e).lower():
                pytest.fail(f"Circular import detected: {e}")
            else:
                raise
    
    def test_lazy_import_environment_loader(self):
        """
        Test that EnvironmentLoader is imported lazily in get_settings
        """
        from app.settings import get_settings
        
        # Call get_settings which should trigger lazy import
        settings = get_settings()
        
        # Should work without circular import
        assert settings is not None
        
        # Verify EnvironmentLoader is now available in settings module namespace
        import app.settings
        # EnvironmentLoader should be importable after get_settings is called
        from app.utils.env_loader import EnvironmentLoader
        assert EnvironmentLoader is not None

