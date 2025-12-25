"""
Unified entry point for gateway service
This script provides a single entry point to start the gateway service
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

import uvicorn
from app.settings import get_settings, reload_settings
from app.utils.env_loader import EnvironmentLoader


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Gateway Service - Unified Entry Point",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start with default settings
  python run.py
  
  # Start with development environment
  python run.py --env dev
  
  # Start with production environment
  python run.py --env prod
  
  # Start with custom host and port
  python run.py --host 0.0.0.0 --port 9000
  
  # Start with reload enabled (development)
  python run.py --env dev --reload
  
  # Start with cluster mode
  python run.py --env prod --deployment-mode cluster
        """
    )
    
    parser.add_argument(
        "--env",
        type=str,
        default=None,
        choices=["default", "dev", "prod"],
        help="Environment name (default: from ENVIRONMENT variable or 'default')"
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default=None,
        help="Host to bind to (default: from settings or '0.0.0.0')"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Port to bind to (default: from settings or 8001)"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload (development mode)"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (default: 1)"
    )
    
    parser.add_argument(
        "--deployment-mode",
        type=str,
        choices=["single", "cluster"],
        default=None,
        help="Deployment mode: single or cluster (default: from settings)"
    )
    
    parser.add_argument(
        "--log-level",
        type=str,
        default=None,
        choices=["debug", "info", "warning", "error", "critical"],
        help="Log level (default: from settings)"
    )
    
    parser.add_argument(
        "--create-env",
        action="store_true",
        help="Create example .env file if it doesn't exist"
    )
    
    parser.add_argument(
        "--init-db",
        action="store_true",
        help="Initialize database before starting"
    )
    
    return parser.parse_args()


def initialize_environment(args: argparse.Namespace) -> None:
    """
    Initialize environment configuration
    
    Args:
        args: Parsed command line arguments
    """
    # Line 78-90: Environment initialization with auto-creation support
    # Reason: Allow automatic creation of .env files if they don't exist
    if args.create_env:
        if args.env:
            deployment_mode = args.deployment_mode or "single"
            EnvironmentLoader.load_environment_with_auto_create(
                env_name=args.env,
                deployment_mode=deployment_mode
            )
        else:
            EnvironmentLoader.load_environment_with_auto_create(
                env_name="default",
                deployment_mode=args.deployment_mode or "single"
            )
    else:
        # Load environment normally
        if args.env:
            EnvironmentLoader.load_environment(env_name=args.env)
        else:
            EnvironmentLoader.load_environment()


def initialize_database(args: argparse.Namespace) -> None:
    """
    Initialize database if requested
    
    Args:
        args: Parsed command line arguments
    """
    # Line 92-105: Database initialization before startup
    # Reason: Allow automatic database initialization on startup
    if args.init_db:
        try:
            import asyncio
            from app.utils.db_init import DatabaseInitializer
            
            print("Initializing database...")
            env_name = args.env or "default"
            result = asyncio.run(DatabaseInitializer.initialize(env_name=env_name))
            
            if result:
                print("Database initialized successfully")
            else:
                print("Warning: Database initialization failed, continuing anyway...")
        except Exception as e:
            print(f"Warning: Database initialization error: {e}, continuing anyway...")


def get_server_config(args: argparse.Namespace):
    """
    Get server configuration from arguments and settings
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Dictionary with server configuration
    """
    # Line 107-125: Server configuration resolution
    # Reason: Allow command line arguments to override settings
    settings = get_settings()
    
    # Reload settings if environment specified
    if args.env:
        settings = reload_settings(env_name=args.env)
    
    config = {
        "app": "app.main:app",
        "host": args.host or settings.host,
        "port": args.port or settings.port,
        "reload": args.reload or settings.debug,
        "workers": args.workers if args.workers > 1 else 1,
        "log_level": args.log_level or settings.log_level.lower(),
    }
    
    return config


def main() -> int:
    """
    Main entry point for gateway service
    
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Line 127-165: Main entry point implementation
    # Reason: Provide unified entry point for starting the gateway service
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Initialize environment
        initialize_environment(args)
        
        # Initialize database if requested
        if args.init_db:
            initialize_database(args)
        
        # Get server configuration
        config = get_server_config(args)
        
        # Print startup information
        print("=" * 60)
        print("Gateway Service - Starting...")
        print("=" * 60)
        print(f"Environment: {args.env or 'default'}")
        print(f"Host: {config['host']}")
        print(f"Port: {config['port']}")
        print(f"Reload: {config['reload']}")
        print(f"Workers: {config['workers']}")
        print(f"Log Level: {config['log_level']}")
        print("=" * 60)
        
        # Start server
        uvicorn.run(**config)
        
        return 0
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        return 0
    except Exception as e:
        print(f"Error starting gateway service: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

