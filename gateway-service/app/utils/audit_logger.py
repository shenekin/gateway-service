"""
Audit logging utility for authentication events

This module provides functionality for logging authentication events
(login, refresh, revoke) to MySQL for audit and compliance purposes.
"""

import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
import asyncmy
from app.settings import get_settings


class AuditLogger:
    """
    Logs authentication events to MySQL for audit purposes
    
    This class handles:
    - Logging login events
    - Logging token refresh events
    - Logging token revocation events
    - Storing audit logs in MySQL
    """
    
    def __init__(self):
        """Initialize audit logger"""
        self.settings = get_settings()
        # Line 25-26: Initialize background tasks set for tracking async audit logging tasks
        # Reason: Track background tasks to prevent garbage collection and ensure they complete
        #         This ensures audit logs are stored even if request finishes quickly
        self._background_tasks: set = set()
    
    async def _get_connection(self):
        """
        Get MySQL connection
        
        Returns:
            MySQL connection object or None if connection fails
        """
        # Line 30-45: MySQL connection for audit logging
        # Reason: Need database connection for storing audit logs
        # Solution: Create connection on-demand for audit logging
        
        try:
            conn = await asyncmy.connect(
                host=self.settings.mysql_host,
                port=self.settings.mysql_port,
                user=self.settings.mysql_user,
                password=self.settings.mysql_password,
                db=self.settings.mysql_database
            )
            return conn
        except Exception:
            return None
    
    async def _store_audit_log_async(
        self,
        event_type: str,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Store audit log in MySQL asynchronously
        
        Args:
            event_type: Type of event (login, refresh, revoke)
            user_id: User identifier
            ip_address: Client IP address
            user_agent: User agent string
            details: Additional event details
        """
        # Line 47-100: Store audit log in MySQL asynchronously
        # Reason: Log authentication events for audit and compliance
        #         Done asynchronously to avoid blocking request processing
        # Solution: Store audit logs in background task
        
        async def store_log_with_error_handling():
            """Store log with error handling"""
            import logging
            logger = logging.getLogger(__name__)
            
            try:
                conn = await self._get_connection()
                if not conn:
                    logger.warning("MySQL connection failed for audit logging")
                    return
                
                async with conn.cursor() as cursor:
                    # Line 70-95: Insert audit log into MySQL
                    # Reason: Store authentication events (login, refresh, revoke) for audit and compliance
                    # Solution: Insert event data with proper error handling
                    
                    sql = """
                        INSERT INTO audit_logs 
                        (event_type, user_id, ip_address, user_agent, details, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    
                    details_json = None
                    if details:
                        import json
                        try:
                            details_json = json.dumps(details)
                        except Exception as e:
                            logger.warning(f"Failed to serialize details to JSON: {e}")
                            details_json = str(details)
                    
                    await cursor.execute(
                        sql,
                        (
                            event_type,
                            user_id,
                            ip_address,
                            user_agent,
                            details_json,
                            datetime.utcnow()
                        )
                    )
                    
                    await conn.commit()
                    logger.info(f"Audit log stored: event_type={event_type}, user_id={user_id}, ip={ip_address}")
                
                conn.close()
            except Exception as e:
                logger.error(f"Error storing audit log: {e}", exc_info=True)
        
        # Create background task
        task = asyncio.create_task(store_log_with_error_handling())
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)
    
    async def log_login(
        self,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log login event
        
        Args:
            user_id: User identifier
            ip_address: Client IP address
            user_agent: User agent string
            details: Additional event details
        """
        # Line 102-115: Log login event
        # Reason: Track user login events for security audit
        await self._store_audit_log_async("login", user_id, ip_address, user_agent, details)
    
    async def log_refresh(
        self,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log token refresh event
        
        Args:
            user_id: User identifier
            ip_address: Client IP address
            user_agent: User agent string
            details: Additional event details
        """
        # Line 117-130: Log refresh event
        # Reason: Track token refresh events for security audit
        await self._store_audit_log_async("refresh", user_id, ip_address, user_agent, details)
    
    async def log_revoke(
        self,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log token revocation event
        
        Args:
            user_id: User identifier
            ip_address: Client IP address
            user_agent: User agent string
            details: Additional event details
        """
        # Line 132-145: Log revoke event
        # Reason: Track token revocation events for security audit
        await self._store_audit_log_async("revoke", user_id, ip_address, user_agent, details)

