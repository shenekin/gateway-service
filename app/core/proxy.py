"""
HTTP proxy service for forwarding requests to backend services
"""

import httpx
from typing import Optional, Dict, Any
from app.models.context import RequestContext
from app.core.discovery import ServiceInstance
from app.core.circuit_breaker import CircuitBreaker
from app.core.retry import RetryHandler
from app.settings import get_settings


class ProxyService:
    """HTTP proxy service for request forwarding"""
    
    def __init__(self):
        """Initialize proxy service"""
        self.settings = get_settings()
        self.client: Optional[httpx.AsyncClient] = None
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.retry_handler = RetryHandler()
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def start(self) -> None:
        """Start proxy service and initialize HTTP client"""
        timeout = httpx.Timeout(30.0, connect=10.0)
        self.client = httpx.AsyncClient(timeout=timeout, follow_redirects=True)
    
    async def close(self) -> None:
        """Close proxy service and cleanup resources"""
        if self.client:
            await self.client.aclose()
    
    def _get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """
        Get or create circuit breaker for service
        
        Args:
            service_name: Name of the service
            
        Returns:
            Circuit breaker instance
        """
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker()
        return self.circuit_breakers[service_name]
    
    async def forward_request(
        self,
        instance: ServiceInstance,
        context: RequestContext,
        method: str,
        path: str,
        headers: Optional[Dict[str, str]] = None,
        query_params: Optional[Dict[str, Any]] = None,
        body: Optional[bytes] = None,
        timeout: Optional[int] = None
    ) -> httpx.Response:
        """
        Forward request to backend service
        
        Args:
            instance: Target service instance
            context: Request context
            method: HTTP method
            path: Request path
            headers: Additional headers
            query_params: Query parameters
            body: Request body
            timeout: Request timeout in seconds
            
        Returns:
            HTTP response
            
        Raises:
            httpx.HTTPError: If request fails
        """
        if not self.client:
            await self.start()
        
        # Build target URL
        target_url = f"{instance.url.rstrip('/')}{path}"
        
        # Merge headers
        forward_headers = context.to_forward_headers()
        if headers:
            forward_headers.update(headers)
        
        # Get circuit breaker for service
        circuit_breaker = self._get_circuit_breaker(context.service_name or "unknown")
        
        # Create request function
        async def make_request():
            request_timeout = timeout or 30.0
            return await self.client.request(
                method=method,
                url=target_url,
                headers=forward_headers,
                params=query_params,
                content=body,
                timeout=request_timeout
            )
        
        # Execute with circuit breaker and retry
        try:
            response = await circuit_breaker.call_async(
                self.retry_handler.execute_async,
                make_request
            )
            return response
        except Exception as e:
            # Mark instance as potentially unhealthy
            instance.failure_count += 1
            raise e
    
    async def forward_streaming_request(
        self,
        instance: ServiceInstance,
        context: RequestContext,
        method: str,
        path: str,
        headers: Optional[Dict[str, str]] = None,
        query_params: Optional[Dict[str, Any]] = None,
        body: Optional[bytes] = None
    ):
        """
        Forward streaming request to backend service
        
        Args:
            instance: Target service instance
            context: Request context
            method: HTTP method
            path: Request path
            headers: Additional headers
            query_params: Query parameters
            body: Request body
            
        Yields:
            Response chunks
        """
        if not self.client:
            await self.start()
        
        target_url = f"{instance.url.rstrip('/')}{path}"
        forward_headers = context.to_forward_headers()
        if headers:
            forward_headers.update(headers)
        
        async with self.client.stream(
            method=method,
            url=target_url,
            headers=forward_headers,
            params=query_params,
            content=body
        ) as response:
            async for chunk in response.aiter_bytes():
                yield chunk

