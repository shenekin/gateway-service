"""
Unit tests for log manager with separate log files
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from app.utils.log_manager import LogManager


class TestLogManager:
    """Test cases for LogManager class"""
    
    def test_log_manager_initialization(self):
        """Test LogManager initialization"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('app.utils.log_manager.get_settings') as mock_settings:
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
                
                log_manager = LogManager()
                
                assert log_manager is not None
                assert len(log_manager.loggers) == 5
    
    def test_log_directory_creation(self):
        """Test that log directory is created if it doesn't exist"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "new_logs"
            
            with patch('app.utils.log_manager.get_settings') as mock_settings:
                settings = Mock()
                settings.log_directory = str(log_dir)
                settings.log_level = "INFO"
                settings.log_format = "text"
                settings.log_request_file = str(log_dir / "request.log")
                settings.log_error_file = str(log_dir / "error.log")
                settings.log_access_file = str(log_dir / "access.log")
                settings.log_audit_file = str(log_dir / "audit.log")
                settings.log_application_file = str(log_dir / "application.log")
                settings.log_max_bytes = 10485760
                settings.log_backup_count = 5
                mock_settings.return_value = settings
                
                log_manager = LogManager()
                
                assert log_dir.exists()
    
    def test_get_logger_request(self):
        """Test getting request logger"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('app.utils.log_manager.get_settings') as mock_settings:
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
                
                log_manager = LogManager()
                logger = log_manager.get_logger(LogManager.LOG_TYPE_REQUEST)
                
                assert logger is not None
                assert logger.name == "gateway.request"
    
    def test_get_logger_error(self):
        """Test getting error logger"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('app.utils.log_manager.get_settings') as mock_settings:
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
                
                log_manager = LogManager()
                logger = log_manager.get_logger(LogManager.LOG_TYPE_ERROR)
                
                assert logger is not None
                assert logger.name == "gateway.error"
    
    def test_log_request(self):
        """Test logging request information"""
        with tempfile.TemporaryDirectory() as tmpdir:
            request_file = Path(tmpdir) / "request.log"
            
            with patch('app.utils.log_manager.get_settings') as mock_settings:
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
                
                log_manager = LogManager()
                log_manager.log_request("Test request", {"request_id": "123"})
                
                # Verify log file was created
                assert request_file.exists()
    
    def test_log_error(self):
        """Test logging error information"""
        with tempfile.TemporaryDirectory() as tmpdir:
            error_file = Path(tmpdir) / "error.log"
            
            with patch('app.utils.log_manager.get_settings') as mock_settings:
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
                
                log_manager = LogManager()
                log_manager.log_error("Test error", {"error_code": "500"})
                
                # Verify error log file was created
                assert error_file.exists()
    
    def test_log_access(self):
        """Test logging access information"""
        with tempfile.TemporaryDirectory() as tmpdir:
            access_file = Path(tmpdir) / "access.log"
            
            with patch('app.utils.log_manager.get_settings') as mock_settings:
                settings = Mock()
                settings.log_directory = tmpdir
                settings.log_level = "INFO"
                settings.log_format = "text"
                settings.log_request_file = str(Path(tmpdir) / "request.log")
                settings.log_error_file = str(Path(tmpdir) / "error.log")
                settings.log_access_file = str(access_file)
                settings.log_audit_file = str(Path(tmpdir) / "audit.log")
                settings.log_application_file = str(Path(tmpdir) / "application.log")
                settings.log_max_bytes = 10485760
                settings.log_backup_count = 5
                mock_settings.return_value = settings
                
                log_manager = LogManager()
                log_manager.log_access("Test access", {"user_id": "123"})
                
                # Verify access log file was created
                assert access_file.exists()
    
    def test_log_audit(self):
        """Test logging audit information"""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit_file = Path(tmpdir) / "audit.log"
            
            with patch('app.utils.log_manager.get_settings') as mock_settings:
                settings = Mock()
                settings.log_directory = tmpdir
                settings.log_level = "INFO"
                settings.log_format = "text"
                settings.log_request_file = str(Path(tmpdir) / "request.log")
                settings.log_error_file = str(Path(tmpdir) / "error.log")
                settings.log_access_file = str(Path(tmpdir) / "access.log")
                settings.log_audit_file = str(audit_file)
                settings.log_application_file = str(Path(tmpdir) / "application.log")
                settings.log_max_bytes = 10485760
                settings.log_backup_count = 5
                mock_settings.return_value = settings
                
                log_manager = LogManager()
                log_manager.log_audit("Test audit", {"action": "login"})
                
                # Verify audit log file was created
                assert audit_file.exists()
    
    def test_log_application(self):
        """Test logging application information"""
        with tempfile.TemporaryDirectory() as tmpdir:
            app_file = Path(tmpdir) / "application.log"
            
            with patch('app.utils.log_manager.get_settings') as mock_settings:
                settings = Mock()
                settings.log_directory = tmpdir
                settings.log_level = "INFO"
                settings.log_format = "text"
                settings.log_request_file = str(Path(tmpdir) / "request.log")
                settings.log_error_file = str(Path(tmpdir) / "error.log")
                settings.log_access_file = str(Path(tmpdir) / "access.log")
                settings.log_audit_file = str(Path(tmpdir) / "audit.log")
                settings.log_application_file = str(app_file)
                settings.log_max_bytes = 10485760
                settings.log_backup_count = 5
                mock_settings.return_value = settings
                
                log_manager = LogManager()
                log_manager.log_application("Test application log", "INFO")
                
                # Verify application log file was created
                assert app_file.exists()
    
    def test_separate_log_files(self):
        """Test that different log types write to separate files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            request_file = Path(tmpdir) / "request.log"
            error_file = Path(tmpdir) / "error.log"
            access_file = Path(tmpdir) / "access.log"
            audit_file = Path(tmpdir) / "audit.log"
            app_file = Path(tmpdir) / "application.log"
            
            with patch('app.utils.log_manager.get_settings') as mock_settings:
                settings = Mock()
                settings.log_directory = tmpdir
                settings.log_level = "INFO"
                settings.log_format = "text"
                settings.log_request_file = str(request_file)
                settings.log_error_file = str(error_file)
                settings.log_access_file = str(access_file)
                settings.log_audit_file = str(audit_file)
                settings.log_application_file = str(app_file)
                settings.log_max_bytes = 10485760
                settings.log_backup_count = 5
                mock_settings.return_value = settings
                
                log_manager = LogManager()
                
                # Log to different types
                log_manager.log_request("Request log")
                log_manager.log_error("Error log")
                log_manager.log_access("Access log")
                log_manager.log_audit("Audit log")
                log_manager.log_application("Application log")
                
                # Verify all files were created
                assert request_file.exists()
                assert error_file.exists()
                assert access_file.exists()
                assert audit_file.exists()
                assert app_file.exists()
                
                # Verify files contain different content
                assert "Request log" in request_file.read_text()
                assert "Error log" in error_file.read_text()
                assert "Access log" in access_file.read_text()
                assert "Audit log" in audit_file.read_text()
                assert "Application log" in app_file.read_text()

