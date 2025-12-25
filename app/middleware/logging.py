"""
Logging middleware for request/response logging with separate log files
"""

import json
import time
from typing import Callable
from fastapi import Request, Response
from datetime import datetime
from app.settings import get_settings
from app.utils.log_manager import LogManager


class LoggingMiddleware:
    """Logging middleware for structured logging with separate log files"""
    
    def __init__(self):
        """Initialize logging middleware"""
        # Line 19-20: Initialize log manager for separate log files
        # Reason: Use LogManager to handle different log types (request, error, access, audit)
        # This ensures different log types are saved to separate .log files
        self.settings = get_settings()
        self.log_manager = LogManager()
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Setup logging configuration"""
        # Line 22-24: Setup basic logging
        # Reason: Maintain backward compatibility while using LogManager
        import logging
        
        # Console handler for immediate output
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, self.settings.log_level.upper(), logging.INFO))
        
        # Use LogManager for file-based logging
        # File handlers are managed by LogManager
    
    def _log_request(self, request: Request, context: dict) -> None:
        """
        Log request information to request.log file
        
        Args:
            request: FastAPI request object
            context: Request context dictionary
        """
        # Line 30-50: Request logging to separate file
        # Reason: Save request logs to request.log file for better log management
        log_data = {
            "request_id": context.get("request_id"),
            "trace_id": context.get("trace_id"),
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "user_id": context.get("user_id"),
            "tenant_id": context.get("tenant_id"),
            "timestamp": datetime.utcnow().isoformat(),
            "log_type": "request"
        }
        
        # Log to request.log file
        self.log_manager.log_request("Request received", log_data)
    
    def _log_response(
        self,
        request: Request,
        response: Response,
        context: dict,
        duration_ms: float
    ) -> None:
        """
        Log response information to appropriate log files
        
        Args:
            request: FastAPI request object
            response: FastAPI response object
            context: Request context dictionary
            duration_ms: Request duration in milliseconds
        """
        # Line 52-85: Response logging with separate files for errors
        # Reason: Save response logs to request.log, errors to error.log
        log_data = {
            "request_id": context.get("request_id"),
            "trace_id": context.get("trace_id"),
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
            "user_id": context.get("user_id"),
            "timestamp": datetime.utcnow().isoformat(),
            "log_type": "response"
        }
        
        # Log response to request.log
        self.log_manager.log_request("Request completed", log_data)
        
        # Log errors to error.log
        if response.status_code >= 400:
            error_data = log_data.copy()
            error_data["error"] = True
            error_data["log_type"] = "error"
            self.log_manager.log_error(
                f"Request failed: {request.method} {request.url.path} - {response.status_code}",
                error_data
            )
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """
        Middleware execution with separate log files
        
        Args:
            request: FastAPI request object
            call_next: Next middleware or route handler
            
        Returns:
            Response
        """
        # Line 87-110: Middleware execution with separate log files
        # Reason: Use LogManager to save different log types to separate files
        start_time = time.time()
        
        # Get context from request state
        context = {
            "request_id": getattr(request.state, "request_id", None),
            "trace_id": getattr(request.state, "trace_id", None),
            "user_id": getattr(request.state, "user_id", None),
            "tenant_id": getattr(request.state, "tenant_id", None)
        }
        
        # Log request to request.log
        self._log_request(request, context)
        
        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log exceptions to error.log
            error_data = context.copy()
            error_data.update({
                "method": request.method,
                "path": request.url.path,
                "exception_type": type(e).__name__,
                "exception_message": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "log_type": "error"
            })
            self.log_manager.log_error(
                f"Request exception: {request.method} {request.url.path}",
                error_data,
                exc_info=True
            )
            raise
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Log response to appropriate files
        self._log_response(request, response, context, duration_ms)
        
        return response

