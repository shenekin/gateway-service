"""
Unit tests for retry handler module
"""

import pytest
from app.core.retry import RetryHandler


def test_retry_handler_success():
    """Test retry handler with successful call"""
    handler = RetryHandler(max_attempts=3)
    
    call_count = 0
    
    def success_func():
        nonlocal call_count
        call_count += 1
        return "success"
    
    result = handler.execute(success_func)
    
    assert result == "success"
    assert call_count == 1


def test_retry_handler_retries_on_failure():
    """Test retry handler retries on failure"""
    handler = RetryHandler(max_attempts=3, backoff_factor=0.1)
    
    call_count = 0
    
    def failing_func():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("Test error")
        return "success"
    
    result = handler.execute(failing_func)
    
    assert result == "success"
    assert call_count == 3


def test_retry_handler_exhausts_retries():
    """Test retry handler exhausts retries"""
    handler = RetryHandler(max_attempts=2, backoff_factor=0.1)
    
    call_count = 0
    
    def always_failing_func():
        nonlocal call_count
        call_count += 1
        raise ValueError("Test error")
    
    with pytest.raises(ValueError):
        handler.execute(always_failing_func)
    
    assert call_count == 2


@pytest.mark.asyncio
async def test_retry_handler_async():
    """Test async retry handler"""
    handler = RetryHandler(max_attempts=3)
    
    call_count = 0
    
    async def success_func():
        nonlocal call_count
        call_count += 1
        return "success"
    
    result = await handler.execute_async(success_func)
    
    assert result == "success"
    assert call_count == 1

