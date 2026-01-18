"""
Unit tests for logging middleware with separate log files
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from fastapi import Request, Response
from app.middleware.logging import LoggingMiddleware


class TestLoggingMiddlewareSeparateFiles:
    """Test cases for logging middleware with separate log files"""
    
    @pytest.mark.asyncio
    async def test_logging_middleware_initialization(self):
        """Test LoggingMiddleware initialization with LogManager"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('app.middleware.logging.get_settings') as mock_settings:
                settings = Mock()
                settings.log_directory = tmpdir
                settings.log_level = "INFO"
                settings.log_format = "text"
                settings.log_request_file = str(Path(tmpdir) / "request.log")
                settings.log_error_file = str(Path(tmpdir) / "error.log")
                settings.log_access_file = str(Path(tmpdir) / "access.log")
                settings.log_audit_file = str(Path(tmpdir) / "audit.log")
                settings.log_application_file = str(Path(tmpdir) / "application.log")
                settings.log_max_bytes = 10485760
                settings.log_backup_count = 5
                mock_settings.return_value = settings
                
                middleware = LoggingMiddleware()
                
                assert middleware is not None
                assert middleware.log_manager is not None
    
    @pytest.mark.asyncio
    async def test_request_logged_to_request_file(self):
        """Test that requests are logged to request.log file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            request_file = Path(tmpdir) / "request.log"
            
            with patch('app.middleware.logging.get_settings') as mock_settings:
                settings = Mock()
                settings.log_directory = tmpdir
                settings.log_level = "INFO"
                settings.log_format = "text"
                settings.log_request_file = str(request_file)
                settings.log_error_file = str(Path(tmpdir) / "error.log")
                settings.log_access_file = str(Path(tmpdir) / "access.log")
                settings.log_audit_file = str(Path(tmpdir) / "audit.log")
                settings.log_application_file = str(Path(tmpdir) / "application.log")
                settings.log_max_bytes = 10485760
                settings.log_backup_count = 5
                mock_settings.return_value = settings
                
                middleware = LoggingMiddleware()
                
                # Mock request
                request = Mock(spec=Request)
                request.method = "GET"
                request.url.path = "/test"
                request.query_params = {}
                request.client = Mock()
                request.client.host = "127.0.0.1"
                request.headers = {"user-agent": "test-agent"}
                request.state.request_id = "req-123"
                request.state.trace_id = "trace-123"
                request.state.user_id = None
                request.state.tenant_id = None
                
                # Mock response
                response = Mock(spec=Response)
                response.status_code = 200
                
                # Mock call_next
                call_next = AsyncMock(return_value=response)
                
                # Execute middleware
                await middleware(request, call_next)
                
                # Verify request was logged to request.log
                assert request_file.exists()
                content = request_file.read_text()
                assert "Request received" in content or "GET" in content
    
    @pytest.mark.asyncio
    async def test_error_response_logged_to_error_file(self):
        """Test that error responses are logged to error.log file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            request_file = Path(tmpdir) / "request.log"
            error_file = Path(tmpdir) / "error.log"
            
            with patch('app.middleware.logging.get_settings') as mock_settings:
                settings = Mock()
                settings.log_directory = tmpdir
                settings.log_level = "INFO"
                settings.log_format = "text"
                settings.log_request_file = str(request_file)
                settings.log_error_file = str(error_file)
                settings.log_access_file = str(Path(tmpdir) / "access.log")
                settings.log_audit_file = str(Path(tmpdir) / "audit.log")
                settings.log_application_file = str(Path(tmpdir) / "application.log")
                settings.log_max_bytes = 10485760
                settings.log_backup_count = 5
                mock_settings.return_value = settings
                
                middleware = LoggingMiddleware()
                
                # Mock request
                request = Mock(spec=Request)
                request.method = "GET"
                request.url.path = "/test"
                request.query_params = {}
                request.client = Mock()
                request.client.host = "127.0.0.1"
                request.headers = {}
                request.state.request_id = "req-123"
                request.state.trace_id = "trace-123"
                request.state.user_id = None
                request.state.tenant_id = None
                
                # Mock error response
                response = Mock(spec=Response)
                response.status_code = 500
                
                # Mock call_next
                call_next = AsyncMock(return_value=response)
                
                # Execute middleware
                await middleware(request, call_next)
                
                # Verify error was logged to error.log
                assert error_file.exists()
                content = error_file.read_text()
                assert "500" in content or "Request failed" in content
    
    @pytest.mark.asyncio
    async def test_exception_logged_to_error_file(self):
        """Test that exceptions are logged to error.log file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            error_file = Path(tmpdir) / "error.log"
            
            with patch('app.middleware.logging.get_settings') as mock_settings:
                settings = Mock()
                settings.log_directory = tmpdir
                settings.log_level = "INFO"
                settings.log_format = "text"
                settings.log_request_file = str(Path(tmpdir) / "request.log")
                settings.log_error_file = str(error_file)
                settings.log_access_file = str(Path(tmpdir) / "access.log")
                settings.log_audit_file = str(Path(tmpdir) / "audit.log")
                settings.log_application_file = str(Path(tmpdir) / "application.log")
                settings.log_max_bytes = 10485760
                settings.log_backup_count = 5
                mock_settings.return_value = settings
                
                middleware = LoggingMiddleware()
                
                # Mock request
                request = Mock(spec=Request)
                request.method = "GET"
                request.url.path = "/test"
                request.query_params = {}
                request.client = Mock()
                request.client.host = "127.0.0.1"
                request.headers = {}
                request.state.request_id = "req-123"
                request.state.trace_id = "trace-123"
                request.state.user_id = None
                request.state.tenant_id = None
                
                # Mock call_next to raise exception
                call_next = AsyncMock(side_effect=ValueError("Test error"))
                
                # Execute middleware and expect exception
                with pytest.raises(ValueError):
                    await middleware(request, call_next)
                
                # Verify exception was logged to error.log
                assert error_file.exists()
                content = error_file.read_text()
                assert "Test error" in content or "ValueError" in content or "Request exception" in content
    
    def test_separate_log_files_created(self):
        """Test that separate log files are created for different log types"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('app.middleware.logging.get_settings') as mock_settings:
                settings = Mock()
                settings.log_directory = tmpdir
                settings.log_level = "INFO"
                settings.log_format = "text"
                settings.log_request_file = str(Path(tmpdir) / "request.log")
                settings.log_error_file = str(Path(tmpdir) / "error.log")
                settings.log_access_file = str(Path(tmpdir) / "access.log")
                settings.log_audit_file = str(Path(tmpdir) / "audit.log")
                settings.log_application_file = str(Path(tmpdir) / "application.log")
                settings.log_max_bytes = 10485760
                settings.log_backup_count = 5
                mock_settings.return_value = settings
                
                middleware = LoggingMiddleware()
                
                # Verify log manager has separate loggers
                assert middleware.log_manager is not None
                assert len(middleware.log_manager.loggers) == 5
                
                # Verify log files can be created
                from app.utils.log_manager import LogManager
                
                log_types = [
                    LogManager.LOG_TYPE_REQUEST,
                    LogManager.LOG_TYPE_ERROR,
                    LogManager.LOG_TYPE_ACCESS,
                    LogManager.LOG_TYPE_AUDIT,
                    LogManager.LOG_TYPE_APPLICATION
                ]
                
                for log_type in log_types:
                    logger = middleware.log_manager.get_logger(log_type)
                    assert logger is not None

