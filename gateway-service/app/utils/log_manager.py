"""
Log manager utility for handling different log types and file handlers
"""

import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional
from app.settings import get_settings


class LogManager:
    """Manager for different log types with separate file handlers"""
    
    # Log type constants
    LOG_TYPE_REQUEST = "request"
    LOG_TYPE_ERROR = "error"
    LOG_TYPE_ACCESS = "access"
    LOG_TYPE_AUDIT = "audit"
    LOG_TYPE_APPLICATION = "application"
    
    def __init__(self):
        """Initialize log manager"""
        self.settings = get_settings()
        self.loggers: dict[str, logging.Logger] = {}
        self._setup_log_directory()
        self._setup_loggers()
    
    def _setup_log_directory(self) -> None:
        """
        Create log directory if it doesn't exist
        
        Line 24-30: Log directory setup
        Reason: Ensure log directory exists before creating log files
        """
        log_dir = Path(self.settings.log_directory)
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            # If permission denied, try to use a fallback directory in the current working directory
            fallback_dir = Path(os.getcwd()) / "logs"
            try:
                fallback_dir.mkdir(parents=True, exist_ok=True)
                # Update settings to use fallback directory
                self.settings.log_directory = str(fallback_dir)
                # Update all log file paths to use fallback directory
                self.settings.log_file_path = str(fallback_dir / "gateway.log")
                self.settings.log_request_file = str(fallback_dir / "request.log")
                self.settings.log_error_file = str(fallback_dir / "error.log")
                self.settings.log_access_file = str(fallback_dir / "access.log")
                self.settings.log_audit_file = str(fallback_dir / "audit.log")
                self.settings.log_application_file = str(fallback_dir / "application.log")
            except Exception as e:
                # If fallback also fails, log warning and continue without file logging
                import logging
                logging.warning(f"Failed to create log directory {log_dir} and fallback {fallback_dir}: {e}. File logging disabled.")
                # Disable file logging by setting paths to None or empty
                self.settings.log_directory = None
    
    def _create_file_handler(
        self,
        log_file_path: str,
        log_level: int,
        formatter: logging.Formatter
    ) -> RotatingFileHandler:
        """
        Create rotating file handler for log file
        
        Args:
            log_file_path: Path to log file
            log_level: Log level
            formatter: Log formatter
            
        Returns:
            RotatingFileHandler instance
        """
        # Line 32-50: File handler creation with rotation
        # Reason: Use rotating file handler to prevent log files from growing too large
        handler = RotatingFileHandler(
            log_file_path,
            maxBytes=self.settings.log_max_bytes,
            backupCount=self.settings.log_backup_count
        )
        handler.setLevel(log_level)
        handler.setFormatter(formatter)
        return handler
    
    def _get_formatter(self) -> logging.Formatter:
        """
        Get log formatter based on configuration
        
        Returns:
            Log formatter instance
        """
        # Line 52-65: Formatter selection
        # Reason: Support both JSON and text formats based on configuration
        if self.settings.log_format == "json":
            try:
                from pythonjsonlogger import jsonlogger
                formatter = jsonlogger.JsonFormatter(
                    "%(asctime)s %(name)s %(levelname)s %(message)s"
                )
            except ImportError:
                # Fallback to standard formatter if pythonjsonlogger not available
                formatter = logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
        else:
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        return formatter
    
    def _setup_loggers(self) -> None:
        """Setup loggers for different log types"""
        # Line 67-100: Logger setup for different log types
        # Reason: Create separate loggers for request, error, access, audit, and application logs
        log_level = getattr(logging, self.settings.log_level.upper(), logging.INFO)
        formatter = self._get_formatter()
        
        # Request logger - for HTTP request/response logging
        request_logger = logging.getLogger("gateway.request")
        request_logger.setLevel(log_level)
        request_handler = self._create_file_handler(
            self.settings.log_request_file,
            log_level,
            formatter
        )
        request_logger.addHandler(request_handler)
        request_logger.propagate = False
        self.loggers[self.LOG_TYPE_REQUEST] = request_logger
        
        # Error logger - for error and exception logging
        error_logger = logging.getLogger("gateway.error")
        error_logger.setLevel(logging.ERROR)
        error_handler = self._create_file_handler(
            self.settings.log_error_file,
            logging.ERROR,
            formatter
        )
        error_logger.addHandler(error_handler)
        error_logger.propagate = False
        self.loggers[self.LOG_TYPE_ERROR] = error_logger
        
        # Access logger - for access control and authentication logging
        access_logger = logging.getLogger("gateway.access")
        access_logger.setLevel(log_level)
        access_handler = self._create_file_handler(
            self.settings.log_access_file,
            log_level,
            formatter
        )
        access_logger.addHandler(access_handler)
        access_logger.propagate = False
        self.loggers[self.LOG_TYPE_ACCESS] = access_logger
        
        # Audit logger - for audit trail and security events
        audit_logger = logging.getLogger("gateway.audit")
        audit_logger.setLevel(log_level)
        audit_handler = self._create_file_handler(
            self.settings.log_audit_file,
            log_level,
            formatter
        )
        audit_logger.addHandler(audit_handler)
        audit_logger.propagate = False
        self.loggers[self.LOG_TYPE_AUDIT] = audit_logger
        
        # Application logger - for general application logging
        app_logger = logging.getLogger("gateway.application")
        app_logger.setLevel(log_level)
        app_handler = self._create_file_handler(
            self.settings.log_application_file,
            log_level,
            formatter
        )
        app_logger.addHandler(app_handler)
        app_logger.propagate = False
        self.loggers[self.LOG_TYPE_APPLICATION] = app_logger
    
    def get_logger(self, log_type: str) -> logging.Logger:
        """
        Get logger for specific log type
        
        Args:
            log_type: Log type (request, error, access, audit, application)
            
        Returns:
            Logger instance
        """
        return self.loggers.get(log_type, self.loggers[self.LOG_TYPE_APPLICATION])
    
    def log_request(self, message: str, extra: Optional[dict] = None) -> None:
        """
        Log request information
        
        Args:
            message: Log message
            extra: Additional context data
        """
        logger = self.get_logger(self.LOG_TYPE_REQUEST)
        if extra:
            logger.info(message, extra=extra)
        else:
            logger.info(message)
    
    def log_error(self, message: str, extra: Optional[dict] = None, exc_info: bool = False) -> None:
        """
        Log error information
        
        Args:
            message: Log message
            extra: Additional context data
            exc_info: Include exception information
        """
        logger = self.get_logger(self.LOG_TYPE_ERROR)
        if extra:
            logger.error(message, extra=extra, exc_info=exc_info)
        else:
            logger.error(message, exc_info=exc_info)
    
    def log_access(self, message: str, extra: Optional[dict] = None) -> None:
        """
        Log access information
        
        Args:
            message: Log message
            extra: Additional context data
        """
        logger = self.get_logger(self.LOG_TYPE_ACCESS)
        if extra:
            logger.info(message, extra=extra)
        else:
            logger.info(message)
    
    def log_audit(self, message: str, extra: Optional[dict] = None) -> None:
        """
        Log audit information
        
        Args:
            message: Log message
            extra: Additional context data
        """
        logger = self.get_logger(self.LOG_TYPE_AUDIT)
        if extra:
            logger.info(message, extra=extra)
        else:
            logger.info(message)
    
    def log_application(self, message: str, level: str = "INFO", extra: Optional[dict] = None) -> None:
        """
        Log application information
        
        Args:
            message: Log message
            level: Log level (DEBUG, INFO, WARNING, ERROR)
            extra: Additional context data
        """
        logger = self.get_logger(self.LOG_TYPE_APPLICATION)
        log_method = getattr(logger, level.lower(), logger.info)
        if extra:
            log_method(message, extra=extra)
        else:
            log_method(message)

