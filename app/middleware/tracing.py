"""
Distributed tracing middleware using OpenTelemetry
"""

from typing import Optional, Callable
from fastapi import Request, FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.trace import Status, StatusCode
from app.settings import get_settings


class TracingMiddleware(BaseHTTPMiddleware):
    """Distributed tracing middleware"""
    
    def __init__(self, app: FastAPI):
        """Initialize tracing middleware
        
        Args:
            app: FastAPI application instance
        """
        super().__init__(app)
        self.settings = get_settings()
        self.tracer: Optional[trace.Tracer] = None
        self._setup_tracing()
    
    def _setup_tracing(self) -> None:
        """Setup OpenTelemetry tracing"""
        if not self.settings.tracing_enabled:
            return
        
        try:
            # Create tracer provider
            provider = TracerProvider()
            trace.set_tracer_provider(provider)
            
            # Add Jaeger exporter
            jaeger_exporter = JaegerExporter(
                agent_host_name=self.settings.jaeger_agent_host,
                agent_port=self.settings.jaeger_agent_port
            )
            
            provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
            
            # Get tracer
            self.tracer = trace.get_tracer(self.settings.service_name)
        except Exception as e:
            # If tracing setup fails, continue without tracing
            self.tracer = None
    
    def get_trace_id(self, request: Request) -> Optional[str]:
        """
        Get trace ID from request headers or generate new one
        
        Args:
            request: FastAPI request object
            
        Returns:
            Trace ID string
        """
        trace_id = request.headers.get("X-Trace-Id")
        if trace_id:
            return trace_id
        
        if self.tracer:
            span = trace.get_current_span()
            if span and span.get_span_context().is_valid:
                return format(span.get_span_context().trace_id, "032x")
        
        return None
    
    def get_span_id(self, request: Request) -> Optional[str]:
        """
        Get span ID from request headers or current span
        
        Args:
            request: FastAPI request object
            
        Returns:
            Span ID string
        """
        span_id = request.headers.get("X-Span-Id")
        if span_id:
            return span_id
        
        if self.tracer:
            span = trace.get_current_span()
            if span and span.get_span_context().is_valid:
                return format(span.get_span_context().span_id, "016x")
        
        return None
    
    async def dispatch(self, request: Request, call_next: Callable) -> any:
        """
        Middleware execution
        
        Args:
            request: FastAPI request object
            call_next: Next middleware or route handler
            
        Returns:
            Response
        """
        if not self.tracer:
            return await call_next(request)
        
        # Create span for request
        with self.tracer.start_as_current_span(
            f"{request.method} {request.url.path}"
        ) as span:
            # Set span attributes
            span.set_attribute("http.method", request.method)
            span.set_attribute("http.url", str(request.url))
            span.set_attribute("http.route", request.url.path)
            
            # Get trace and span IDs
            trace_id = format(span.get_span_context().trace_id, "032x")
            span_id = format(span.get_span_context().span_id, "016x")
            
            # Store in request state
            request.state.trace_id = trace_id
            request.state.span_id = span_id
            
            try:
                # Process request
                response = await call_next(request)
                
                # Set status
                span.set_status(Status(StatusCode.OK))
                span.set_attribute("http.status_code", response.status_code)
                
                return response
            except Exception as e:
                # Record exception
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise

