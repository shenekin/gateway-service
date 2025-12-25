"""
Circuit breaker pattern implementation for fault tolerance
"""

import time
from typing import Optional, Callable, Any
from enum import Enum
from app.settings import get_settings


class CircuitState(str, Enum):
    """Circuit breaker states"""
    
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """Circuit breaker for protecting services from cascading failures"""
    
    def __init__(
        self,
        failure_threshold: Optional[int] = None,
        timeout_seconds: Optional[int] = None,
        half_open_max_calls: Optional[int] = None
    ):
        """
        Initialize circuit breaker
        
        Args:
            failure_threshold: Number of failures before opening circuit
            timeout_seconds: Time to wait before attempting half-open
            half_open_max_calls: Max calls in half-open state
        """
        self.settings = get_settings()
        self.failure_threshold = failure_threshold or self.settings.circuit_breaker_failure_threshold
        self.timeout_seconds = timeout_seconds or self.settings.circuit_breaker_timeout_seconds
        self.half_open_max_calls = half_open_max_calls or self.settings.circuit_breaker_half_open_max_calls
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.half_open_calls = 0
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If circuit is open or function fails
        """
        if not self.settings.circuit_breaker_enabled:
            return func(*args, **kwargs)
        
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.half_open_calls = 0
            else:
                raise RuntimeError("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute async function with circuit breaker protection
        
        Args:
            func: Async function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If circuit is open or function fails
        """
        if not self.settings.circuit_breaker_enabled:
            return await func(*args, **kwargs)
        
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.half_open_calls = 0
            else:
                raise RuntimeError("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self) -> None:
        """Handle successful call"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            self.half_open_calls += 1
            
            if self.success_count >= self.half_open_max_calls:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                self.half_open_calls = 0
        else:
            self.failure_count = 0
    
    def _on_failure(self) -> None:
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            self.half_open_calls = 0
        elif self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
    
    def _should_attempt_reset(self) -> bool:
        """
        Check if circuit breaker should attempt reset
        
        Returns:
            True if should attempt reset
        """
        if self.last_failure_time is None:
            return True
        
        elapsed = time.time() - self.last_failure_time
        return elapsed >= self.timeout_seconds
    
    def reset(self) -> None:
        """Manually reset circuit breaker to closed state"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.half_open_calls = 0
        self.last_failure_time = None
    
    def get_state(self) -> CircuitState:
        """
        Get current circuit breaker state
        
        Returns:
            Current state
        """
        return self.state

