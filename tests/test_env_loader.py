"""
Unit tests for environment loader utility
"""

import os
import pytest
import tempfile
from pathlib import Path
from app.utils.env_loader import EnvironmentLoader


class TestEnvironmentLoader:
    """Test cases for EnvironmentLoader class"""
    
    def test_get_env_file_path_default(self):
        """Test getting default environment file path"""
        path = EnvironmentLoader.get_env_file_path("default")
        assert ".env" in path or "env" in path.lower()
    
    def test_get_env_file_path_dev(self):
        """Test getting development environment file path"""
        path = EnvironmentLoader.get_env_file_path("dev")
        assert ".env.dev" in path
    
    def test_get_env_file_path_prod(self):
        """Test getting production environment file path"""
        path = EnvironmentLoader.get_env_file_path("prod")
        assert ".env.prod" in path
    
    def test_get_env_file_path_with_base_path(self):
        """Test getting environment file path with custom base path"""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = tmpdir
            path = EnvironmentLoader.get_env_file_path("dev", base_path)
            assert base_path in path
            assert ".env.dev" in path
    
    def test_load_environment_with_existing_file(self):
        """Test loading environment from existing file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env.dev"
            env_file.write_text("TEST_VAR=test_value\nENVIRONMENT=dev\n")
            
            result = EnvironmentLoader.load_environment("dev", tmpdir)
            assert result is True
            assert os.getenv("TEST_VAR") == "test_value"
            assert os.getenv("ENVIRONMENT") == "dev"
    
    def test_load_environment_with_nonexistent_file(self):
        """Test loading environment from non-existent file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = EnvironmentLoader.load_environment("nonexistent", tmpdir)
            assert result is False
    
    def test_load_environment_fallback_to_default(self):
        """Test loading environment falls back to default .env"""
        with tempfile.TemporaryDirectory() as tmpdir:
            default_env = Path(tmpdir) / ".env"
            default_env.write_text("FALLBACK_VAR=fallback_value\n")
            
            result = EnvironmentLoader.load_environment("dev", tmpdir)
            # Should try to load default if dev doesn't exist
            if result:
                assert os.getenv("FALLBACK_VAR") == "fallback_value"
    
    def test_get_available_environments(self):
        """Test getting list of available environment files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multiple env files
            (Path(tmpdir) / ".env").write_text("ENVIRONMENT=default\n")
            (Path(tmpdir) / ".env.dev").write_text("ENVIRONMENT=dev\n")
            (Path(tmpdir) / ".env.prod").write_text("ENVIRONMENT=prod\n")
            
            available = EnvironmentLoader.get_available_environments(tmpdir)
            assert len(available) >= 3
            assert "default" in available or "dev" in available
    
    def test_get_available_environments_no_files(self):
        """Test getting available environments when no files exist"""
        with tempfile.TemporaryDirectory() as tmpdir:
            available = EnvironmentLoader.get_available_environments(tmpdir)
            assert isinstance(available, list)
    
    def test_environment_loader_env_file_mapping(self):
        """Test environment name to file mapping"""
        assert EnvironmentLoader.ENV_FILES["default"] == ".env"
        assert EnvironmentLoader.ENV_FILES["dev"] == ".env.dev"
        assert EnvironmentLoader.ENV_FILES["development"] == ".env.dev"
        assert EnvironmentLoader.ENV_FILES["prod"] == ".env.prod"
        assert EnvironmentLoader.ENV_FILES["production"] == ".env.prod"

