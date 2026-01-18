"""
Database initialization script for gateway service
This script can be run manually or automatically to initialize the database
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.settings import get_settings
import asyncmy


async def create_database(settings) -> bool:
    """
    Create database if it doesn't exist
    
    Args:
        settings: Settings instance
        
    Returns:
        True if successful
    """
    try:
        # Connect without specifying database
        conn = await asyncmy.connect(
            host=settings.mysql_host,
            port=settings.mysql_port,
            user=settings.mysql_user,
            password=settings.mysql_password
        )
        
        cursor = await conn.cursor()
        
        # Create database
        await cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {settings.mysql_database} "
            f"DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        
        await cursor.close()
        conn.close()
        
        print(f"Database '{settings.mysql_database}' created or already exists")
        return True
    except Exception as e:
        print(f"Error creating database: {e}")
        return False


async def execute_sql_file(settings, sql_file_path: Path) -> bool:
    """
    Execute SQL file to create tables
    
    Args:
        settings: Settings instance
        sql_file_path: Path to SQL file
        
    Returns:
        True if successful
    """
    try:
        if not sql_file_path.exists():
            print(f"SQL file not found: {sql_file_path}")
            return False
        
        # Read SQL file
        sql_content = sql_file_path.read_text()
        
        # Connect to database
        conn = await asyncmy.connect(
            host=settings.mysql_host,
            port=settings.mysql_port,
            user=settings.mysql_user,
            password=settings.mysql_password,
            db=settings.mysql_database
        )
        
        cursor = await conn.cursor()
        
        # Execute SQL statements
        # Split by semicolon and execute each statement
        statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]
        
        for statement in statements:
            if statement:
                try:
                    await cursor.execute(statement)
                except Exception as e:
                    # Ignore errors for IF NOT EXISTS statements
                    if "already exists" not in str(e).lower():
                        print(f"Warning executing statement: {e}")
        
        await conn.commit()
        await cursor.close()
        conn.close()
        
        print(f"SQL file '{sql_file_path}' executed successfully")
        return True
    except Exception as e:
        print(f"Error executing SQL file: {e}")
        return False


async def initialize_database(env_name: Optional[str] = None, sql_file_path: Optional[Path] = None) -> bool:
    """
    Initialize database: create database and tables
    
    Args:
        env_name: Environment name (default, dev, prod)
        sql_file_path: Path to SQL file (default: scripts/database/init_database.sql)
        
    Returns:
        True if successful
    """
    print("Starting database initialization...")
    
    # Load settings
    settings = get_settings(env_name=env_name)
    
    # Create database
    if not await create_database(settings):
        return False
    
    # Execute SQL file
    if sql_file_path is None:
        sql_file_path = Path(__file__).parent / "init_database.sql"
    
    if not await execute_sql_file(settings, sql_file_path):
        return False
    
    print("Database initialization completed successfully")
    return True


async def check_database_connection(env_name: Optional[str] = None) -> bool:
    """
    Check database connection
    
    Args:
        env_name: Environment name
        
    Returns:
        True if connection successful
    """
    try:
        settings = get_settings(env_name=env_name)
        
        conn = await asyncmy.connect(
            host=settings.mysql_host,
            port=settings.mysql_port,
            user=settings.mysql_user,
            password=settings.mysql_password,
            db=settings.mysql_database
        )
        
        cursor = await conn.cursor()
        await cursor.execute("SELECT 1")
        result = await cursor.fetchone()
        
        await cursor.close()
        conn.close()
        
        print(f"Database connection successful: {settings.mysql_database}")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


def main():
    """Main function for command-line execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize gateway service database")
    parser.add_argument(
        "--env",
        type=str,
        default=None,
        help="Environment name (default, dev, prod)"
    )
    parser.add_argument(
        "--sql-file",
        type=str,
        default=None,
        help="Path to SQL file"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check database connection"
    )
    
    args = parser.parse_args()
    
    if args.check_only:
        result = asyncio.run(check_database_connection(args.env))
        sys.exit(0 if result else 1)
    else:
        sql_path = Path(args.sql_file) if args.sql_file else None
        result = asyncio.run(initialize_database(args.env, sql_path))
        sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()

