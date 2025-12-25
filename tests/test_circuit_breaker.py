"""
Unit tests for circuit breaker module
"""

import pytest
from app.core.circuit_breaker import CircuitBreaker, CircuitState


def test_circuit_breaker_closed_state():
    """Test circuit breaker in closed state"""
    cb = CircuitBreaker(failure_threshold=3, timeout_seconds=60)
    
    assert cb.get_state() == CircuitState.CLOSED
    
    def success_func():
        return "success"
    
    result = cb.call(success_func)
    assert result == "success"
    assert cb.get_state() == CircuitState.CLOSED


def test_circuit_breaker_opens_after_failures():
    """Test circuit breaker opens after threshold failures"""
    cb = CircuitBreaker(failure_threshold=2, timeout_seconds=60)
    
    def failing_func():
        raise ValueError("Test error")
    
    # First failure
    with pytest.raises(ValueError):
        cb.call(failing_func)
    assert cb.get_state() == CircuitState.CLOSED
    
    # Second failure - should open
    with pytest.raises(ValueError):
        cb.call(failing_func)
    assert cb.get_state() == CircuitState.OPEN


def test_circuit_breaker_open_rejects_requests():
    """Test circuit breaker rejects requests when open"""
    cb = CircuitBreaker(failure_threshold=1, timeout_seconds=60)
    
    def failing_func():
        raise ValueError("Test error")
    
    # Open the circuit
    with pytest.raises(ValueError):
        cb.call(failing_func)
    
    # Should reject new requests
    with pytest.raises(RuntimeError, match="Circuit breaker is OPEN"):
        cb.call(lambda: "should not execute")


@pytest.mark.asyncio
async def test_circuit_breaker_async():
    """Test async circuit breaker"""
    cb = CircuitBreaker(failure_threshold=2, timeout_seconds=60)
    
    async def success_func():
        return "success"
    
    result = await cb.call_async(success_func)
    assert result == "success"


def test_circuit_breaker_reset():
    """Test manual circuit breaker reset"""
    cb = CircuitBreaker(failure_threshold=1, timeout_seconds=60)
    
    def failing_func():
        raise ValueError("Test error")
    
    # Open the circuit
    with pytest.raises(ValueError):
        cb.call(failing_func)
    
    assert cb.get_state() == CircuitState.OPEN
    
    # Reset
    cb.reset()
    assert cb.get_state() == CircuitState.CLOSED
    assert cb.failure_count == 0

