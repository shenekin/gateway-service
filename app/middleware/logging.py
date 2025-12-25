"""
Logging middleware for request/response logging
"""

import json
import time
from typing import Callable
from fastapi import Request, Response
from datetime import datetime
from app.settings import get_settings


class LoggingMiddleware:
    """Logging middleware for structured logging"""
    
    def __init__(self):
        """Initialize logging middleware"""
        self.settings = get_settings()
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Setup logging configuration"""
        import logging
        
        log_level = getattr(logging, self.settings.log_level.upper(), logging.INFO)
        
        if self.settings.log_format == "json":
            import logging.config
            logging.config.dictConfig({
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "json": {
                        "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                        "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
                    }
                },
                "handlers": {
                    "console": {
                        "class": "logging.StreamHandler",
                        "formatter": "json",
                        "level": log_level
                    }
                },
                "root": {
                    "level": log_level,
                    "handlers": ["console"]
                }
            })
        
        self.logger = logging.getLogger("gateway")
    
    def _log_request(self, request: Request, context: dict) -> None:
        """
        Log request information
        
        Args:
            request: FastAPI request object
            context: Request context dictionary
        """
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
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if self.settings.log_format == "json":
            self.logger.info("Request received", extra=log_data)
        else:
            self.logger.info(f"Request: {request.method} {request.url.path}")
    
    def _log_response(
        self,
        request: Request,
        response: Response,
        context: dict,
        duration_ms: float
    ) -> None:
        """
        Log response information
        
        Args:
            request: FastAPI request object
            response: FastAPI response object
            context: Request context dictionary
            duration_ms: Request duration in milliseconds
        """
        log_data = {
            "request_id": context.get("request_id"),
            "trace_id": context.get("trace_id"),
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
            "user_id": context.get("user_id"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if response.status_code >= 400:
            log_data["error"] = True
        
        if self.settings.log_format == "json":
            self.logger.info("Request completed", extra=log_data)
        else:
            self.logger.info(
                f"Response: {request.method} {request.url.path} "
                f"{response.status_code} ({duration_ms}ms)"
            )
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """
        Middleware execution
        
        Args:
            request: FastAPI request object
            call_next: Next middleware or route handler
            
        Returns:
            Response
        """
        start_time = time.time()
        
        # Get context from request state
        context = {
            "request_id": getattr(request.state, "request_id", None),
            "trace_id": getattr(request.state, "trace_id", None),
            "user_id": getattr(request.state, "user_id", None),
            "tenant_id": getattr(request.state, "tenant_id", None)
        }
        
        # Log request
        self._log_request(request, context)
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Log response
        self._log_response(request, response, context, duration_ms)
        
        return response

