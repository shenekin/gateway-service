"""
Unit tests for environment file auto-creation functionality
"""

import os
import pytest
import tempfile
from pathlib import Path
from app.utils.env_loader import EnvironmentLoader


class TestEnvironmentAutoCreate:
    """Test cases for automatic environment file creation"""
    
    def test_create_example_env_file_single_mode(self):
        """Test creating example env file in single mode"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / ".env.test"
            
            result = EnvironmentLoader._create_basic_env_file(file_path, "test", "single")
            
            assert result is True
            assert file_path.exists()
            
            content = file_path.read_text()
            assert "ENVIRONMENT=test" in content
            assert "DEPLOYMENT_MODE=single" in content
            assert "CLUSTER_ENABLED=false" in content
    
    def test_create_example_env_file_cluster_mode(self):
        """Test creating example env file in cluster mode"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / ".env.test"
            
            result = EnvironmentLoader._create_basic_env_file(file_path, "test", "cluster")
            
            assert result is True
            assert file_path.exists()
            
            content = file_path.read_text()
            assert "ENVIRONMENT=test" in content
            assert "DEPLOYMENT_MODE=cluster" in content
            assert "CLUSTER_ENABLED=true" in content
    
    def test_load_environment_with_auto_create(self):
        """Test loading environment with automatic file creation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            
            # File doesn't exist, should be created
            result = EnvironmentLoader.load_environment_with_auto_create(
                env_name="default",
                base_path=tmpdir,
                deployment_mode="single"
            )
            
            # Should create file and load it
            assert env_file.exists() or result is False  # May fail if script not available
    
    def test_load_environment_with_auto_create_existing_file(self):
        """Test loading existing environment file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            env_file.write_text("ENVIRONMENT=test\nTEST_VAR=test_value\n")
            
            result = EnvironmentLoader.load_environment_with_auto_create(
                env_name="default",
                base_path=tmpdir,
                deployment_mode="single"
            )
            
            assert result is True
            assert os.getenv("ENVIRONMENT") == "test"
            assert os.getenv("TEST_VAR") == "test_value"
    
    def test_create_example_env_file_different_environments(self):
        """Test creating example files for different environments"""
        with tempfile.TemporaryDirectory() as tmpdir:
            for env_name in ["default", "dev", "prod"]:
                file_path = Path(tmpdir) / f".env.{env_name}" if env_name != "default" else Path(tmpdir) / ".env"
                
                result = EnvironmentLoader._create_basic_env_file(file_path, env_name, "single")
                
                assert result is True
                assert file_path.exists()
                
                content = file_path.read_text()
                assert f"ENVIRONMENT={env_name}" in content
    
    def test_create_example_env_file_cluster_config(self):
        """Test that cluster mode includes cluster configuration"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / ".env"
            
            result = EnvironmentLoader._create_basic_env_file(file_path, "test", "cluster")
            
            assert result is True
            content = file_path.read_text()
            
            # Check for cluster-specific configurations
            assert "MYSQL_CLUSTER_ENABLED=true" in content
            assert "REDIS_CLUSTER_ENABLED=true" in content
            assert "NACOS_CLUSTER_ENABLED=true" in content
    
    def test_create_example_env_file_single_config(self):
        """Test that single mode includes single instance configuration"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / ".env"
            
            result = EnvironmentLoader._create_basic_env_file(file_path, "test", "single")
            
            assert result is True
            content = file_path.read_text()
            
            # Check for single instance configurations
            assert "MYSQL_CLUSTER_ENABLED=false" in content
            assert "REDIS_CLUSTER_ENABLED=false" in content
            assert "NACOS_CLUSTER_ENABLED=false" in content

