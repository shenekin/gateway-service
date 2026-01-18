"""
Unit tests for external services verification script
Tests verify that the service verification script correctly checks all external dependencies
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from pathlib import Path

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.verify_external_services import ServiceVerifier


class TestServiceVerifier:
    """Test cases for ServiceVerifier class"""
    
    @pytest.fixture
    def verifier(self):
        """Create ServiceVerifier instance"""
        return ServiceVerifier()
    
    @pytest.mark.asyncio
    async def test_check_redis_success(self, verifier):
        """
        Test Redis connection check when Redis is available
        
        Test Case: Redis connection successful
        Expected: Returns (Redis, True, success message)
        """
        # Line 15-30: Test Redis connection success
        # Reason: Verify Redis connection check works correctly when Redis is available
        with patch("scripts.verify_external_services.aioredis") as mock_redis:
            mock_client = AsyncMock()
            mock_client.ping = AsyncMock()
            mock_client.aclose = AsyncMock()
            mock_redis.from_url = AsyncMock(return_value=mock_client)
            
            result = await verifier.check_redis()
            
            assert result[0] == "Redis"
            assert result[1] is True
            assert "Connected" in result[2]
            mock_client.ping.assert_called_once()
            mock_client.aclose.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_check_redis_failure(self, verifier):
        """
        Test Redis connection check when Redis is unavailable
        
        Test Case: Redis connection failed
        Expected: Returns (Redis, False, error message)
        """
        # Line 32-45: Test Redis connection failure
        # Reason: Verify Redis connection check handles failures correctly
        with patch("scripts.verify_external_services.aioredis") as mock_redis:
            mock_redis.from_url = AsyncMock(side_effect=Exception("Connection refused"))
            
            result = await verifier.check_redis()
            
            assert result[0] == "Redis"
            assert result[1] is False
            assert "Connection failed" in result[2]
    
    @pytest.mark.asyncio
    async def test_check_mysql_success(self, verifier):
        """
        Test MySQL connection check when MySQL is available
        
        Test Case: MySQL connection successful
        Expected: Returns (MySQL, True, success message)
        """
        # Line 47-65: Test MySQL connection success
        # Reason: Verify MySQL connection check works correctly when MySQL is available
        with patch("scripts.verify_external_services.asyncmy") as mock_mysql:
            mock_conn = AsyncMock()
            mock_cursor = AsyncMock()
            mock_cursor.execute = AsyncMock()
            mock_cursor.fetchone = AsyncMock(return_value=(1,))
            mock_conn.cursor = AsyncMock(return_value=mock_cursor)
            mock_conn.close = Mock()
            mock_mysql.connect = AsyncMock(return_value=mock_conn)
            
            result = await verifier.check_mysql()
            
            assert result[0] == "MySQL"
            assert result[1] is True
            assert "Connected" in result[2]
            mock_cursor.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_check_mysql_failure(self, verifier):
        """
        Test MySQL connection check when MySQL is unavailable
        
        Test Case: MySQL connection failed
        Expected: Returns (MySQL, False, error message)
        """
        # Line 67-80: Test MySQL connection failure
        # Reason: Verify MySQL connection check handles failures correctly
        with patch("scripts.verify_external_services.asyncmy") as mock_mysql:
            mock_mysql.connect = AsyncMock(side_effect=Exception("Connection refused"))
            
            result = await verifier.check_mysql()
            
            assert result[0] == "MySQL"
            assert result[1] is False
            assert "Connection failed" in result[2]
    
    @pytest.mark.asyncio
    async def test_check_database_initialized_success(self, verifier):
        """
        Test database initialization check when all tables exist
        
        Test Case: All required tables exist
        Expected: Returns (Database Schema, True, success message)
        """
        # Line 82-105: Test database initialization check success
        # Reason: Verify database schema check works correctly when all tables exist
        with patch("scripts.verify_external_services.asyncmy") as mock_mysql:
            mock_conn = AsyncMock()
            mock_cursor = AsyncMock()
            mock_cursor.execute = AsyncMock()
            mock_cursor.fetchone = AsyncMock(return_value=(6,))  # All 6 tables exist
            mock_conn.cursor = AsyncMock(return_value=mock_cursor)
            mock_conn.close = Mock()
            mock_mysql.connect = AsyncMock(return_value=mock_conn)
            
            result = await verifier.check_database_initialized()
            
            assert result[0] == "Database Schema"
            assert result[1] is True
            assert "All" in result[2] and "tables exist" in result[2]
    
    @pytest.mark.asyncio
    async def test_check_database_initialized_partial(self, verifier):
        """
        Test database initialization check when some tables are missing
        
        Test Case: Only some tables exist
        Expected: Returns (Database Schema, False, warning message)
        """
        # Line 107-125: Test database initialization check partial
        # Reason: Verify database schema check detects missing tables
        with patch("scripts.verify_external_services.asyncmy") as mock_mysql:
            mock_conn = AsyncMock()
            mock_cursor = AsyncMock()
            mock_cursor.execute = AsyncMock()
            mock_cursor.fetchone = AsyncMock(return_value=(3,))  # Only 3 tables exist
            mock_conn.cursor = AsyncMock(return_value=mock_cursor)
            mock_conn.close = Mock()
            mock_mysql.connect = AsyncMock(return_value=mock_conn)
            
            result = await verifier.check_database_initialized()
            
            assert result[0] == "Database Schema"
            assert result[1] is False
            assert "Only" in result[2] and "tables found" in result[2]
    
    @pytest.mark.asyncio
    async def test_check_service_discovery_static(self, verifier):
        """
        Test service discovery check for static mode
        
        Test Case: Static service discovery with services.yaml exists
        Expected: Returns (Service Discovery (Static), True, success message)
        """
        # Line 127-145: Test static service discovery check
        # Reason: Verify static service discovery check works correctly
        verifier.settings.service_discovery_type = "static"
        
        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.return_value = True
            
            result = await verifier.check_service_discovery()
            
            assert result[0] == "Service Discovery (Static)"
            assert result[1] is True
            assert "static configuration" in result[2]
    
    @pytest.mark.asyncio
    async def test_check_service_discovery_nacos_success(self, verifier):
        """
        Test service discovery check for Nacos when available
        
        Test Case: Nacos service discovery connection successful
        Expected: Returns (Nacos, True, success message)
        """
        # Line 147-165: Test Nacos service discovery check success
        # Reason: Verify Nacos service discovery check works correctly
        verifier.settings.service_discovery_type = "nacos"
        verifier.settings.nacos_server_addresses = "localhost:8848"
        
        with patch("scripts.verify_external_services.httpx") as mock_httpx:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_httpx.AsyncClient = Mock(return_value=mock_client)
            
            result = await verifier.check_service_discovery()
            
            assert result[0] == "Nacos"
            assert result[1] is True
            assert "Connected" in result[2]
    
    @pytest.mark.asyncio
    async def test_check_service_discovery_nacos_failure(self, verifier):
        """
        Test service discovery check for Nacos when unavailable
        
        Test Case: Nacos service discovery connection failed
        Expected: Returns (Nacos, False, error message)
        """
        # Line 167-180: Test Nacos service discovery check failure
        # Reason: Verify Nacos service discovery check handles failures correctly
        verifier.settings.service_discovery_type = "nacos"
        verifier.settings.nacos_server_addresses = "localhost:8848"
        
        with patch("scripts.verify_external_services.httpx") as mock_httpx:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(side_effect=Exception("Connection refused"))
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_httpx.AsyncClient = Mock(return_value=mock_client)
            
            result = await verifier.check_service_discovery()
            
            assert result[0] == "Nacos"
            assert result[1] is False
            assert "Connection failed" in result[2]
    
    @pytest.mark.asyncio
    async def test_check_jaeger_disabled(self, verifier):
        """
        Test Jaeger check when tracing is disabled
        
        Test Case: Tracing disabled
        Expected: Returns (Jaeger, True, not required message)
        """
        # Line 182-195: Test Jaeger check when disabled
        # Reason: Verify Jaeger check handles disabled tracing correctly
        verifier.settings.tracing_enabled = False
        
        result = await verifier.check_jaeger()
        
        assert result[0] == "Jaeger"
        assert result[1] is True
        assert "disabled" in result[2].lower()
    
    @pytest.mark.asyncio
    async def test_check_jaeger_enabled_success(self, verifier):
        """
        Test Jaeger check when tracing is enabled and Jaeger is available
        
        Test Case: Jaeger available
        Expected: Returns (Jaeger, True, success message)
        """
        # Line 197-215: Test Jaeger check when enabled and available
        # Reason: Verify Jaeger check works correctly when Jaeger is available
        verifier.settings.tracing_enabled = True
        verifier.settings.jaeger_agent_host = "localhost"
        
        with patch("scripts.verify_external_services.httpx") as mock_httpx:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_httpx.AsyncClient = Mock(return_value=mock_client)
            
            result = await verifier.check_jaeger()
            
            assert result[0] == "Jaeger"
            assert result[1] is True
            assert "Connected" in result[2]
    
    def test_check_log_directory_success(self, verifier, tmp_path):
        """
        Test log directory check when directory is writable
        
        Test Case: Log directory writable
        Expected: Returns (Log Directory, True, success message)
        """
        # Line 217-235: Test log directory check success
        # Reason: Verify log directory check works correctly when directory is writable
        verifier.settings.log_directory = str(tmp_path)
        
        result = verifier.check_log_directory()
        
        assert result[0] == "Log Directory"
        assert result[1] is True
        assert "writable" in result[2]
    
    def test_check_log_directory_failure(self, verifier):
        """
        Test log directory check when directory is not writable
        
        Test Case: Log directory not writable
        Expected: Returns (Log Directory, False, error message)
        """
        # Line 237-250: Test log directory check failure
        # Reason: Verify log directory check handles failures correctly
        verifier.settings.log_directory = "/root/readonly/directory"
        
        result = verifier.check_log_directory()
        
        assert result[0] == "Log Directory"
        assert result[1] is False
        assert "Not writable" in result[2] or "failed" in result[2].lower()
    
    @pytest.mark.asyncio
    async def test_check_backend_services_success(self, verifier):
        """
        Test backend services check when services are available
        
        Test Case: Backend services found and healthy
        Expected: Returns (Backend Services, True, success message)
        """
        # Line 252-275: Test backend services check success
        # Reason: Verify backend services check works correctly when services are available
        with patch("scripts.verify_external_services.create_service_discovery") as mock_create:
            mock_discovery = AsyncMock()
            mock_instance = Mock()
            mock_instance.healthy = True
            mock_discovery.get_instances = AsyncMock(return_value=[mock_instance, mock_instance])
            mock_create.return_value = mock_discovery
            
            result = await verifier.check_backend_services()
            
            assert result[0] == "Backend Services"
            assert result[1] is True
            assert "Found" in result[2] and "healthy" in result[2]
    
    @pytest.mark.asyncio
    async def test_check_backend_services_no_instances(self, verifier):
        """
        Test backend services check when no instances found
        
        Test Case: No backend service instances found
        Expected: Returns (Backend Services, False, error message)
        """
        # Line 277-295: Test backend services check no instances
        # Reason: Verify backend services check handles missing services correctly
        with patch("scripts.verify_external_services.create_service_discovery") as mock_create:
            mock_discovery = AsyncMock()
            mock_discovery.get_instances = AsyncMock(return_value=[])
            mock_create.return_value = mock_discovery
            
            result = await verifier.check_backend_services()
            
            assert result[0] == "Backend Services"
            assert result[1] is False
            assert "No backend service instances found" in result[2]
    
    @pytest.mark.asyncio
    async def test_verify_all_success(self, verifier):
        """
        Test comprehensive verification when all services are available
        
        Test Case: All required services available
        Expected: Returns dict with can_start=True
        """
        # Line 297-330: Test comprehensive verification success
        # Reason: Verify complete service verification works correctly
        with patch.object(verifier, "check_redis", return_value=("Redis", True, "Connected")):
            with patch.object(verifier, "check_mysql", return_value=("MySQL", True, "Connected")):
                with patch.object(verifier, "check_database_initialized", return_value=("Database Schema", True, "All tables exist")):
                    with patch.object(verifier, "check_log_directory", return_value=("Log Directory", True, "Writable")):
                        with patch.object(verifier, "check_service_discovery", return_value=("Service Discovery", True, "Available")):
                            with patch.object(verifier, "check_jaeger", return_value=("Jaeger", True, "Available")):
                                with patch.object(verifier, "check_backend_services", return_value=("Backend Services", True, "Available")):
                                    
                                    result = await verifier.verify_all()
                                    
                                    assert result["required_passed"] is True
                                    assert result["can_start"] is True
                                    assert len(result["results"]) == 7
    
    @pytest.mark.asyncio
    async def test_verify_all_failure(self, verifier):
        """
        Test comprehensive verification when required services are unavailable
        
        Test Case: Some required services unavailable
        Expected: Returns dict with can_start=False
        """
        # Line 332-350: Test comprehensive verification failure
        # Reason: Verify complete service verification detects missing required services
        with patch.object(verifier, "check_redis", return_value=("Redis", False, "Connection failed")):
            with patch.object(verifier, "check_mysql", return_value=("MySQL", True, "Connected")):
                with patch.object(verifier, "check_database_initialized", return_value=("Database Schema", True, "All tables exist")):
                    with patch.object(verifier, "check_log_directory", return_value=("Log Directory", True, "Writable")):
                        with patch.object(verifier, "check_service_discovery", return_value=("Service Discovery", True, "Available")):
                            with patch.object(verifier, "check_jaeger", return_value=("Jaeger", True, "Available")):
                                with patch.object(verifier, "check_backend_services", return_value=("Backend Services", True, "Available")):
                                    
                                    result = await verifier.verify_all()
                                    
                                    assert result["required_passed"] is False
                                    assert result["can_start"] is False
                                    assert len(result["results"]) == 7

