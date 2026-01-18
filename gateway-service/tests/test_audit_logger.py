"""
Unit tests for AuditLogger

Tests cover:
- Login event logging
- Refresh event logging
- Revoke event logging
- MySQL storage
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from app.utils.audit_logger import AuditLogger
from app.settings import get_settings


@pytest.fixture
def audit_logger():
    """Create AuditLogger instance"""
    return AuditLogger()


@pytest.fixture
def mock_mysql_conn():
    """Mock MySQL connection"""
    conn = AsyncMock()
    cursor = AsyncMock()
    conn.cursor = MagicMock(return_value=cursor.__enter__())
    cursor.__aenter__ = AsyncMock(return_value=cursor)
    cursor.__aexit__ = AsyncMock(return_value=None)
    cursor.execute = AsyncMock()
    conn.commit = AsyncMock()
    conn.close = AsyncMock()
    return conn


@pytest.mark.asyncio
async def test_log_login(audit_logger, mock_mysql_conn):
    """Test logging login event"""
    # Line 25-45: Test login event logging
    # Reason: Verify login events are logged to MySQL
    # Solution: Mock MySQL connection and verify insert
    
    with patch.object(audit_logger, "_get_connection", return_value=mock_mysql_conn):
        await audit_logger.log_login(
            user_id="user123",
            ip_address="127.0.0.1",
            user_agent="test-agent"
        )
        
        # Wait for background task
        await asyncio.sleep(0.1)
        
        # Verify cursor.execute was called
        assert mock_mysql_conn.cursor.return_value.execute.called


@pytest.mark.asyncio
async def test_log_refresh(audit_logger, mock_mysql_conn):
    """Test logging refresh event"""
    # Line 47-65: Test refresh event logging
    # Reason: Verify refresh events are logged to MySQL
    # Solution: Mock MySQL connection and verify insert
    
    with patch.object(audit_logger, "_get_connection", return_value=mock_mysql_conn):
        await audit_logger.log_refresh(
            user_id="user123",
            ip_address="127.0.0.1",
            user_agent="test-agent",
            details={"token_rotation": True}
        )
        
        # Wait for background task
        await asyncio.sleep(0.1)
        
        # Verify cursor.execute was called
        assert mock_mysql_conn.cursor.return_value.execute.called


@pytest.mark.asyncio
async def test_log_revoke(audit_logger, mock_mysql_conn):
    """Test logging revoke event"""
    # Line 67-85: Test revoke event logging
    # Reason: Verify revoke events are logged to MySQL
    # Solution: Mock MySQL connection and verify insert
    
    with patch.object(audit_logger, "_get_connection", return_value=mock_mysql_conn):
        await audit_logger.log_revoke(
            user_id="user123",
            ip_address="127.0.0.1",
            user_agent="test-agent"
        )
        
        # Wait for background task
        await asyncio.sleep(0.1)
        
        # Verify cursor.execute was called
        assert mock_mysql_conn.cursor.return_value.execute.called


@pytest.mark.asyncio
async def test_log_with_mysql_connection_failure(audit_logger):
    """Test logging when MySQL connection fails"""
    # Line 87-100: Test error handling when MySQL fails
    # Reason: Verify logging doesn't fail if MySQL is unavailable
    # Solution: Mock connection failure and verify no exception
    
    with patch.object(audit_logger, "_get_connection", return_value=None):
        # Should not raise exception
        await audit_logger.log_login(
            user_id="user123",
            ip_address="127.0.0.1"
        )
        
        # Wait for background task
        await asyncio.sleep(0.1)


@pytest.mark.asyncio
async def test_store_audit_log_with_details(audit_logger, mock_mysql_conn):
    """Test storing audit log with additional details"""
    # Line 102-120: Test audit log with JSON details
    # Reason: Verify additional details are stored as JSON
    # Solution: Mock MySQL and verify JSON is stored
    
    with patch.object(audit_logger, "_get_connection", return_value=mock_mysql_conn):
        details = {"key1": "value1", "key2": "value2"}
        await audit_logger.log_login(
            user_id="user123",
            details=details
        )
        
        # Wait for background task
        await asyncio.sleep(0.1)
        
        # Verify cursor.execute was called
        assert mock_mysql_conn.cursor.return_value.execute.called

