"""
Database initialization utility
"""

import asyncio
from pathlib import Path
from typing import Optional
from app.settings import get_settings
import asyncmy


class DatabaseInitializer:
    """Utility class for database initialization"""
    
    @staticmethod
    async def create_database(settings) -> bool:
        """
        Create database if it doesn't exist
        
        Args:
            settings: Settings instance
            
        Returns:
            True if successful
        """
        try:
            conn = await asyncmy.connect(
                host=settings.mysql_host,
                port=settings.mysql_port,
                user=settings.mysql_user,
                password=settings.mysql_password
            )
            
            cursor = await conn.cursor()
            await cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS {settings.mysql_database} "
                f"DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            await cursor.close()
            conn.close()
            
            return True
        except Exception as e:
            print(f"Error creating database: {e}")
            return False
    
    @staticmethod
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
                return False
            
            sql_content = sql_file_path.read_text()
            
            conn = await asyncmy.connect(
                host=settings.mysql_host,
                port=settings.mysql_port,
                user=settings.mysql_user,
                password=settings.mysql_password,
                db=settings.mysql_database
            )
            
            cursor = await conn.cursor()
            statements = [
                s.strip() for s in sql_content.split(';')
                if s.strip() and not s.strip().startswith('--')
            ]
            
            for statement in statements:
                if statement:
                    try:
                        await cursor.execute(statement)
                    except Exception:
                        pass  # Ignore errors for IF NOT EXISTS
            
            await conn.commit()
            await cursor.close()
            conn.close()
            
            return True
        except Exception as e:
            print(f"Error executing SQL file: {e}")
            return False
    
    @staticmethod
    async def initialize(env_name: Optional[str] = None, sql_file_path: Optional[Path] = None) -> bool:
        """
        Initialize database: create database and tables
        
        Args:
            env_name: Environment name
            sql_file_path: Path to SQL file
            
        Returns:
            True if successful
        """
        settings = get_settings(env_name=env_name)
        
        if not await DatabaseInitializer.create_database(settings):
            return False
        
        if sql_file_path is None:
            sql_file_path = Path(__file__).parent.parent.parent / "scripts" / "database" / "init_database.sql"
        
        return await DatabaseInitializer.execute_sql_file(settings, sql_file_path)
    
    @staticmethod
    async def check_connection(env_name: Optional[str] = None) -> bool:
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
            await cursor.fetchone()
            
            await cursor.close()
            conn.close()
            
            return True
        except Exception:
            return False

