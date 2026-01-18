"""
Unit tests for database initialization functionality
"""

import tempfile
import pytest
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from app.utils.db_init import DatabaseInitializer


class TestDatabaseInitializer:
    """Test cases for DatabaseInitializer class"""
    
    @pytest.mark.asyncio
    async def test_create_database_success(self):
        """Test successful database creation"""
        settings = Mock()
        settings.mysql_host = "localhost"
        settings.mysql_port = 3306
        settings.mysql_user = "test_user"
        settings.mysql_password = "test_password"
        settings.mysql_database = "test_db"
        
        with patch("app.utils.db_init.asyncmy.connect") as mock_connect:
            mock_conn = AsyncMock()
            mock_cursor = AsyncMock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            
            result = await DatabaseInitializer.create_database(settings)
            
            assert result is True
            mock_connect.assert_called_once()
            mock_cursor.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_database_failure(self):
        """Test database creation failure"""
        settings = Mock()
        settings.mysql_host = "localhost"
        settings.mysql_port = 3306
        settings.mysql_user = "test_user"
        settings.mysql_password = "test_password"
        settings.mysql_database = "test_db"
        
        with patch("app.utils.db_init.asyncmy.connect", side_effect=Exception("Connection failed")):
            result = await DatabaseInitializer.create_database(settings)
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_execute_sql_file_success(self):
        """Test successful SQL file execution"""
        settings = Mock()
        settings.mysql_host = "localhost"
        settings.mysql_port = 3306
        settings.mysql_user = "test_user"
        settings.mysql_password = "test_password"
        settings.mysql_database = "test_db"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            sql_file = Path(tmpdir) / "test.sql"
            sql_file.write_text("CREATE TABLE test (id INT);")
            
            with patch("app.utils.db_init.asyncmy.connect") as mock_connect:
                mock_conn = AsyncMock()
                mock_cursor = AsyncMock()
                mock_connect.return_value = mock_conn
                mock_conn.cursor.return_value = mock_cursor
                
                result = await DatabaseInitializer.execute_sql_file(settings, sql_file)
                
                assert result is True
                mock_cursor.execute.assert_called()
    
    @pytest.mark.asyncio
    async def test_execute_sql_file_not_found(self):
        """Test SQL file not found"""
        settings = Mock()
        sql_file = Path("/nonexistent/file.sql")
        
        result = await DatabaseInitializer.execute_sql_file(settings, sql_file)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_check_connection_success(self):
        """Test successful database connection check"""
        settings = Mock()
        settings.mysql_host = "localhost"
        settings.mysql_port = 3306
        settings.mysql_user = "test_user"
        settings.mysql_password = "test_password"
        settings.mysql_database = "test_db"
        
        with patch("app.utils.db_init.asyncmy.connect") as mock_connect:
            mock_conn = AsyncMock()
            mock_cursor = AsyncMock()
            mock_cursor.fetchone.return_value = (1,)
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            
            result = await DatabaseInitializer.check_connection(settings)
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_check_connection_failure(self):
        """Test database connection check failure"""
        settings = Mock()
        settings.mysql_host = "localhost"
        settings.mysql_port = 3306
        settings.mysql_user = "test_user"
        settings.mysql_password = "test_password"
        settings.mysql_database = "test_db"
        
        with patch("app.utils.db_init.asyncmy.connect", side_effect=Exception("Connection failed")):
            result = await DatabaseInitializer.check_connection(settings)
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_initialize_with_default_sql_file(self):
        """Test initialization with default SQL file path"""
        with patch("app.utils.db_init.get_settings") as mock_settings, \
             patch("app.utils.db_init.DatabaseInitializer.create_database") as mock_create, \
             patch("app.utils.db_init.DatabaseInitializer.execute_sql_file") as mock_execute:
            
            mock_settings.return_value = Mock()
            mock_create.return_value = True
            mock_execute.return_value = True
            
            result = await DatabaseInitializer.initialize()
            
            assert result is True
            mock_create.assert_called_once()
            mock_execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_initialize_with_custom_sql_file(self):
        """Test initialization with custom SQL file path"""
        with tempfile.TemporaryDirectory() as tmpdir:
            sql_file = Path(tmpdir) / "custom.sql"
            sql_file.write_text("CREATE TABLE test (id INT);")
            
            with patch("app.utils.db_init.get_settings") as mock_settings, \
                 patch("app.utils.db_init.DatabaseInitializer.create_database") as mock_create, \
                 patch("app.utils.db_init.DatabaseInitializer.execute_sql_file") as mock_execute:
                
                mock_settings.return_value = Mock()
                mock_create.return_value = True
                mock_execute.return_value = True
                
                result = await DatabaseInitializer.initialize(sql_file_path=sql_file)
                
                assert result is True
                mock_execute.assert_called_once_with(mock_settings.return_value, sql_file)
    
    @pytest.mark.asyncio
    async def test_initialize_database_creation_failure(self):
        """Test initialization when database creation fails"""
        with patch("app.utils.db_init.get_settings") as mock_settings, \
             patch("app.utils.db_init.DatabaseInitializer.create_database") as mock_create:
            
            mock_settings.return_value = Mock()
            mock_create.return_value = False
            
            result = await DatabaseInitializer.initialize()
            
            assert result is False

