"""
Retry mechanism with exponential backoff
"""

import asyncio
import time
from typing import Callable, Any, Optional, List, Type
from app.settings import get_settings


class RetryHandler:
    """Retry handler with exponential backoff"""
    
    def __init__(
        self,
        max_attempts: Optional[int] = None,
        backoff_factor: Optional[float] = None,
        max_delay_seconds: Optional[int] = None,
        retryable_exceptions: Optional[List[Type[Exception]]] = None
    ):
        """
        Initialize retry handler
        
        Args:
            max_attempts: Maximum number of retry attempts
            backoff_factor: Exponential backoff multiplier
            max_delay_seconds: Maximum delay between retries
            retryable_exceptions: List of exception types to retry
        """
        self.settings = get_settings()
        self.max_attempts = max_attempts or self.settings.retry_max_attempts
        self.backoff_factor = backoff_factor or self.settings.retry_backoff_factor
        self.max_delay_seconds = max_delay_seconds or self.settings.retry_max_delay_seconds
        self.retryable_exceptions = retryable_exceptions or [Exception]
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with retry logic
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: Last exception if all retries fail
        """
        if not self.settings.retry_enabled:
            return func(*args, **kwargs)
        
        last_exception = None
        
        for attempt in range(self.max_attempts):
            try:
                return func(*args, **kwargs)
            except tuple(self.retryable_exceptions) as e:
                last_exception = e
                
                if attempt < self.max_attempts - 1:
                    delay = min(
                        self.backoff_factor ** attempt,
                        self.max_delay_seconds
                    )
                    time.sleep(delay)
                else:
                    raise last_exception
        
        if last_exception:
            raise last_exception
    
    async def execute_async(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute async function with retry logic
        
        Args:
            func: Async function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: Last exception if all retries fail
        """
        if not self.settings.retry_enabled:
            return await func(*args, **kwargs)
        
        last_exception = None
        
        for attempt in range(self.max_attempts):
            try:
                return await func(*args, **kwargs)
            except tuple(self.retryable_exceptions) as e:
                last_exception = e
                
                if attempt < self.max_attempts - 1:
                    delay = min(
                        self.backoff_factor ** attempt,
                        self.max_delay_seconds
                    )
                    await asyncio.sleep(delay)
                else:
                    raise last_exception
        
        if last_exception:
            raise last_exception
    
    def should_retry(self, exception: Exception) -> bool:
        """
        Check if exception should trigger retry
        
        Args:
            exception: Exception to check
            
        Returns:
            True if should retry
        """
        return isinstance(exception, tuple(self.retryable_exceptions))

