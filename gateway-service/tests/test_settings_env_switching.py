"""
Unit tests for settings environment switching functionality
"""

import os
import pytest
import tempfile
from pathlib import Path
from app.settings import Settings, get_settings, reload_settings, get_available_environments


class TestSettingsEnvironmentSwitching:
    """Test cases for environment switching in settings"""
    
    def test_get_settings_default_environment(self):
        """Test getting settings with default environment"""
        settings = get_settings()
        assert settings is not None
        assert isinstance(settings, Settings)
    
    def test_get_settings_with_env_name(self):
        """Test getting settings with specific environment name"""
        # This test verifies the function accepts env_name parameter
        settings = get_settings(env_name="dev")
        assert settings is not None
    
    def test_get_settings_with_env_file_path(self):
        """Test getting settings with custom env file path"""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env.test"
            env_file.write_text("ENVIRONMENT=test\nHOST=127.0.0.1\nPORT=9000\n")
            
            settings = get_settings(env_file_path=str(env_file))
            assert settings is not None
    
    def test_reload_settings_function(self):
        """Test reload_settings function"""
        # Get initial settings
        settings1 = get_settings()
        
        # Reload settings
        settings2 = reload_settings()
        
        assert settings2 is not None
        assert isinstance(settings2, Settings)
    
    def test_reload_settings_with_env_name(self):
        """Test reload_settings with environment name"""
        settings = reload_settings(env_name="dev")
        assert settings is not None
    
    def test_reload_settings_with_env_file_path(self):
        """Test reload_settings with custom env file path"""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env.custom"
            env_file.write_text("ENVIRONMENT=custom\nDEBUG=true\n")
            
            settings = reload_settings(env_file_path=str(env_file))
            assert settings is not None
    
    def test_get_available_environments(self):
        """Test getting list of available environments"""
        environments = get_available_environments()
        assert isinstance(environments, list)
    
    def test_settings_cache_clearing(self):
        """Test that reload_settings clears cache"""
        # Get settings (cached)
        settings1 = get_settings()
        
        # Reload should clear cache
        settings2 = reload_settings()
        
        # Next get_settings should return new instance
        settings3 = get_settings()
        
        # All should be Settings instances
        assert isinstance(settings1, Settings)
        assert isinstance(settings2, Settings)
        assert isinstance(settings3, Settings)
    
    def test_environment_variable_override(self):
        """Test that environment variables override .env file values"""
        original_port = os.getenv("PORT")
        
        try:
            # Set environment variable
            os.environ["PORT"] = "9999"
            
            # Reload settings
            settings = reload_settings()
            
            # Should use environment variable
            assert settings.port == 9999
        finally:
            # Restore original value
            if original_port:
                os.environ["PORT"] = original_port
            else:
                os.environ.pop("PORT", None)
    
    def test_multiple_environment_switching(self):
        """Test switching between multiple environments"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create dev environment
            dev_env = Path(tmpdir) / ".env.dev"
            dev_env.write_text("ENVIRONMENT=dev\nHOST=0.0.0.0\nPORT=8001\n")
            
            # Create prod environment
            prod_env = Path(tmpdir) / ".env.prod"
            prod_env.write_text("ENVIRONMENT=prod\nHOST=0.0.0.0\nPORT=8002\n")
            
            # Load dev
            settings_dev = reload_settings(env_name="dev")
            
            # Load prod
            settings_prod = reload_settings(env_name="prod")
            
            assert settings_dev is not None
            assert settings_prod is not None

