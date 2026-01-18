"""
Environment file loader utility for multi-environment support
"""

import os
import sys
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class EnvironmentLoader:
    """Utility class for loading environment configuration files"""
    
    # Supported environment files
    ENV_FILES = {
        "default": ".env",
        "dev": ".env.dev",
        "development": ".env.dev",
        "prod": ".env.prod",
        "production": ".env.prod"
    }
    
    @classmethod
    def get_env_file_path(cls, env_name: Optional[str] = None, base_path: Optional[str] = None) -> str:
        """
        Get environment file path based on environment name
        
        Args:
            env_name: Environment name (default, dev, prod)
            base_path: Base directory path for .env files
            
        Returns:
            Path to environment file
        """
        if env_name is None:
            env_name = os.getenv("ENVIRONMENT", "default").lower()
        
        env_file = cls.ENV_FILES.get(env_name, ".env")
        
        if base_path:
            return str(Path(base_path) / env_file)
        
        # Try project root directory
        current_dir = Path(__file__).parent.parent.parent
        env_path = current_dir / env_file
        
        if env_path.exists():
            return str(env_path)
        
        # Fallback to current directory
        return env_file
    
    @classmethod
    def load_environment(cls, env_name: Optional[str] = None, base_path: Optional[str] = None) -> bool:
        """
        Load environment variables from specified environment file
        
        Args:
            env_name: Environment name (default, dev, prod)
            base_path: Base directory path for .env files
            
        Returns:
            True if file loaded successfully, False otherwise
        """
        env_file_path = cls.get_env_file_path(env_name, base_path)
        
        if not os.path.exists(env_file_path):
            # If specific env file doesn't exist, try default .env
            if env_name and env_name != "default":
                default_path = cls.get_env_file_path("default", base_path)
                if os.path.exists(default_path):
                    env_file_path = default_path
                else:
                    return False
            else:
                return False
        
        # Load environment variables
        load_dotenv(env_file_path, override=True)
        return True
    
    @classmethod
    def get_available_environments(cls, base_path: Optional[str] = None) -> list[str]:
        """
        Get list of available environment files
        
        Args:
            base_path: Base directory path for .env files
            
        Returns:
            List of available environment names
        """
        available = []
        
        if base_path:
            search_dir = Path(base_path)
        else:
            search_dir = Path(__file__).parent.parent.parent
        
        for env_name, env_file in cls.ENV_FILES.items():
            env_path = search_dir / env_file
            if env_path.exists():
                available.append(env_name)
        
        return list(set(available))  # Remove duplicates
    
    @classmethod
    def create_example_env_file(cls, env_name: str, deployment_mode: str = "single", base_path: Optional[str] = None) -> bool:
        """
        Create example environment file with configuration
        
        Args:
            env_name: Environment name (default, dev, prod)
            deployment_mode: Deployment mode (single, cluster)
            base_path: Base directory path for .env files
            
        Returns:
            True if file created successfully
        """
        # Line 108-120: Added method to automatically create example .env files
        # Reason: Allow automatic creation of example configuration files when they don't exist
        try:
            if base_path:
                base_dir = Path(base_path)
            else:
                base_dir = Path(__file__).parent.parent.parent
            
            env_file = cls.ENV_FILES.get(env_name, ".env")
            file_path = base_dir / env_file
            
            # Import create script function
            scripts_path = base_dir / "scripts" / "create_env_examples.py"
            if scripts_path.exists():
                # Use the create script
                import importlib.util
                spec = importlib.util.spec_from_file_location("create_env_examples", scripts_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Call the create function
                module.create_env_example_file(file_path, env_name, deployment_mode)
                return True
            else:
                # Fallback: create basic .env file
                return cls._create_basic_env_file(file_path, env_name, deployment_mode)
        except Exception as e:
            print(f"Error creating example env file: {e}", file=sys.stderr)
            return False
    
    @classmethod
    def _create_basic_env_file(cls, file_path: Path, env_name: str, deployment_mode: str) -> bool:
        """
        Create basic environment file as fallback
        
        Args:
            file_path: Path to .env file
            env_name: Environment name
            deployment_mode: Deployment mode
            
        Returns:
            True if successful
        """
        # Line 122-150: Added fallback method to create basic .env file
        # Reason: Provide basic configuration when create script is not available
        is_cluster = deployment_mode == "cluster"
        
        content = f"""# Environment: {env_name}
# Deployment Mode: {deployment_mode}
# Auto-generated example file

ENVIRONMENT={env_name}
DEPLOYMENT_MODE={deployment_mode}
CLUSTER_ENABLED={'true' if is_cluster else 'false'}

# MySQL Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=gateway_user
MYSQL_PASSWORD=gateway_password
MYSQL_DATABASE=gateway_db
MYSQL_CLUSTER_ENABLED={'true' if is_cluster else 'false'}

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_CLUSTER_ENABLED={'true' if is_cluster else 'false'}

# Nacos Configuration
NACOS_SERVER_ADDRESSES=localhost:8848
NACOS_CLUSTER_ENABLED={'true' if is_cluster else 'false'}
"""
        
        try:
            file_path.write_text(content)
            return True
        except Exception:
            return False
    
    @classmethod
    def load_environment_with_auto_create(cls, env_name: Optional[str] = None, base_path: Optional[str] = None, deployment_mode: str = "single") -> bool:
        """
        Load environment file, creating example file if it doesn't exist
        
        Args:
            env_name: Environment name (default, dev, prod)
            base_path: Base directory path for .env files
            deployment_mode: Deployment mode for auto-creation (single, cluster)
            
        Returns:
            True if file loaded or created successfully
        """
        # Line 152-175: Added method to load environment with automatic file creation
        # Reason: Automatically create example .env files when they don't exist
        env_file_path = cls.get_env_file_path(env_name, base_path)
        
        if not os.path.exists(env_file_path):
            # Try to create example file
            if env_name is None:
                env_name = os.getenv("ENVIRONMENT", "default").lower()
            
            print(f"Environment file not found: {env_file_path}")
            print(f"Creating example file with {deployment_mode} mode...")
            
            if cls.create_example_env_file(env_name, deployment_mode, base_path):
                print(f"Example environment file created: {env_file_path}")
            else:
                print(f"Warning: Could not create example file: {env_file_path}")
                return False
        
        # Load environment variables
        load_dotenv(env_file_path, override=True)
        return True

