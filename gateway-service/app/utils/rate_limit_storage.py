"""
Rate limit storage utility for MySQL integration
This module provides MySQL storage for rate limit records while Redis handles fast rate limit checking
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from app.settings import get_settings
import asyncmy


class RateLimitStorage:
    """
    MySQL storage for rate limit records
    
    This class provides persistent storage for rate limit records in MySQL.
    Redis is used for fast rate limit checking, while MySQL stores records
    for audit, analytics, and historical tracking.
    """
    
    def __init__(self):
        """Initialize rate limit storage"""
        self.settings = get_settings()
        self._connection_pool: Optional[Any] = None
    
    async def _get_connection(self):
        """
        Get MySQL connection
        
        Returns:
            MySQL connection object
            
        Raises:
            Exception: If connection fails
        """
        # Line 30-45: MySQL connection management
        # Reason: Need database connection for storing rate limit records
        #         Connection is created on-demand to avoid keeping connections open
        try:
            conn = await asyncmy.connect(
                host=self.settings.mysql_host,
                port=self.settings.mysql_port,
                user=self.settings.mysql_user,
                password=self.settings.mysql_password,
                db=self.settings.mysql_database
            )
            return conn
        except Exception as e:
            # Log error but don't fail - rate limiting should still work with Redis only
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"MySQL connection error: {e}")
            return None
    
    async def store_rate_limit_record(
        self,
        identifier: str,
        window_type: str,
        request_count: int,
        window_start: datetime,
        window_end: datetime,
        route_path: Optional[str] = None
    ) -> bool:
        """
        Store rate limit record in MySQL
        
        This method stores rate limit records for audit and analytics.
        It uses INSERT ... ON DUPLICATE KEY UPDATE to handle concurrent updates.
        
        Args:
            identifier: Rate limit identifier (user_id, ip, api_key)
            window_type: Time window type (minute, hour, day)
            request_count: Number of requests in current window
            window_start: Window start timestamp
            window_end: Window end timestamp
            route_path: Optional route path
            
        Returns:
            True if successful, False otherwise
        """
        # Line 47-95: Store rate limit record in MySQL
        # Reason: Persist rate limit records for audit, analytics, and historical tracking
        #         This complements Redis which handles fast rate limit checking
        # Solution: Store records in MySQL table with upsert logic for concurrent updates
        
        conn = None
        try:
            conn = await self._get_connection()
            if not conn:
                # Line 90-94: Connection failed - log and return False
                # Reason: MySQL connection failed, but rate limiting should continue with Redis
                import logging
                logger = logging.getLogger(__name__)
                logger.warning("MySQL connection failed for rate limit storage")
                return False
            
            async with conn.cursor() as cursor:
                # Use INSERT ... ON DUPLICATE KEY UPDATE for atomic upsert
                # This handles concurrent requests updating the same record
                # Line 98-109: Updated SQL to use alias syntax instead of deprecated VALUES() function
                # Reason: MySQL 8.0.19+ deprecates VALUES() function in favor of alias syntax
                #         This prevents deprecation warnings and ensures future compatibility
                # Solution: Use AS alias and reference alias.col instead of VALUES(col)
                sql = """
                    INSERT INTO rate_limit_records 
                    (identifier, window_type, route_path, request_count, window_start, window_end)
                    VALUES (%s, %s, %s, %s, %s, %s) AS new
                    ON DUPLICATE KEY UPDATE
                        request_count = new.request_count,
                        window_end = new.window_end,
                        updated_at = CURRENT_TIMESTAMP
                """
                
                await cursor.execute(
                    sql,
                    (
                        identifier,
                        window_type,
                        route_path,
                        request_count,
                        window_start,
                        window_end
                    )
                )
                
                await conn.commit()
                
                # Line 130-136: Log successful storage for debugging
                # Reason: Help verify that records are being stored correctly
                import logging
                logger = logging.getLogger(__name__)
                logger.debug(
                    f"Stored rate limit record: identifier={identifier}, "
                    f"window={window_type}, count={request_count}"
                )
                
                return True
        except Exception as e:
            # If MySQL fails, log but don't fail - Redis rate limiting still works
            # This ensures rate limiting continues even if MySQL is unavailable
            import logging
            logger = logging.getLogger(__name__)
            logger.error(
                f"Error storing rate limit record in MySQL: {e}",
                exc_info=True
            )
            if conn:
                try:
                    await conn.rollback()
                except Exception:
                    pass
            return False
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
    
    async def get_rate_limit_record(
        self,
        identifier: str,
        window_type: str,
        window_start: datetime,
        route_path: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get rate limit record from MySQL
        
        Args:
            identifier: Rate limit identifier
            window_type: Time window type
            window_start: Window start timestamp
            route_path: Optional route path
            
        Returns:
            Rate limit record dictionary or None if not found
        """
        # Line 97-135: Get rate limit record from MySQL
        # Reason: Retrieve rate limit records for analysis or recovery
        #         Can be used to sync Redis state from MySQL if needed
        
        conn = None
        try:
            conn = await self._get_connection()
            if not conn:
                return None
            
            async with conn.cursor() as cursor:
                sql = """
                    SELECT id, identifier, window_type, route_path, request_count,
                           window_start, window_end, created_at, updated_at
                    FROM rate_limit_records
                    WHERE identifier = %s 
                      AND window_type = %s 
                      AND window_start = %s
                      AND (route_path = %s OR (route_path IS NULL AND %s IS NULL))
                    LIMIT 1
                """
                
                await cursor.execute(
                    sql,
                    (identifier, window_type, window_start, route_path, route_path)
                )
                
                result = await cursor.fetchone()
                
                if result:
                    return {
                        "id": result[0],
                        "identifier": result[1],
                        "window_type": result[2],
                        "route_path": result[3],
                        "request_count": result[4],
                        "window_start": result[5],
                        "window_end": result[6],
                        "created_at": result[7],
                        "updated_at": result[8]
                    }
                
                return None
        except Exception:
            return None
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
    
    async def get_rate_limit_history(
        self,
        identifier: Optional[str] = None,
        window_type: Optional[str] = None,
        route_path: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get rate limit history from MySQL
        
        Args:
            identifier: Optional identifier filter
            window_type: Optional window type filter
            route_path: Optional route path filter
            start_time: Optional start time filter
            end_time: Optional end time filter
            limit: Maximum number of records to return
            
        Returns:
            List of rate limit records
        """
        # Line 137-195: Get rate limit history from MySQL
        # Reason: Query rate limit records for analytics and reporting
        #         Provides historical data for understanding rate limit patterns
        
        conn = None
        try:
            conn = await self._get_connection()
            if not conn:
                return []
            
            async with conn.cursor() as cursor:
                # Build dynamic query based on filters
                conditions = []
                params = []
                
                if identifier:
                    conditions.append("identifier = %s")
                    params.append(identifier)
                
                if window_type:
                    conditions.append("window_type = %s")
                    params.append(window_type)
                
                if route_path:
                    conditions.append("route_path = %s")
                    params.append(route_path)
                
                if start_time:
                    conditions.append("window_start >= %s")
                    params.append(start_time)
                
                if end_time:
                    conditions.append("window_end <= %s")
                    params.append(end_time)
                
                where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
                
                sql = f"""
                    SELECT id, identifier, window_type, route_path, request_count,
                           window_start, window_end, created_at, updated_at
                    FROM rate_limit_records
                    {where_clause}
                    ORDER BY window_start DESC, updated_at DESC
                    LIMIT %s
                """
                
                params.append(limit)
                
                await cursor.execute(sql, params)
                
                results = await cursor.fetchall()
                
                records = []
                for result in results:
                    records.append({
                        "id": result[0],
                        "identifier": result[1],
                        "window_type": result[2],
                        "route_path": result[3],
                        "request_count": result[4],
                        "window_start": result[5],
                        "window_end": result[6],
                        "created_at": result[7],
                        "updated_at": result[8]
                    })
                
                return records
        except Exception:
            return []
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
    
    async def cleanup_old_records(self, days: int = 30) -> int:
        """
        Clean up old rate limit records
        
        Args:
            days: Number of days to keep records (default: 30)
            
        Returns:
            Number of records deleted
        """
        # Line 197-230: Cleanup old rate limit records
        # Reason: Remove old records to prevent database growth
        #         Keeps database size manageable while preserving recent history
        
        conn = None
        try:
            conn = await self._get_connection()
            if not conn:
                return 0
            
            async with conn.cursor() as cursor:
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                
                sql = """
                    DELETE FROM rate_limit_records
                    WHERE window_end < %s
                """
                
                await cursor.execute(sql, (cutoff_date,))
                deleted_count = cursor.rowcount
                
                await conn.commit()
                
                return deleted_count
        except Exception:
            if conn:
                try:
                    await conn.rollback()
                except Exception:
                    pass
            return 0
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
    
    async def get_statistics(
        self,
        identifier: Optional[str] = None,
        window_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get rate limit statistics
        
        Args:
            identifier: Optional identifier filter
            window_type: Optional window type filter
            start_time: Optional start time filter
            end_time: Optional end time filter
            
        Returns:
            Dictionary with statistics
        """
        # Line 232-295: Get rate limit statistics
        # Reason: Provide aggregated statistics for monitoring and analysis
        #         Helps understand rate limit usage patterns
        
        conn = None
        try:
            conn = await self._get_connection()
            if not conn:
                return {
                    "total_requests": 0,
                    "unique_identifiers": 0,
                    "average_requests_per_identifier": 0,
                    "max_requests": 0,
                    "min_requests": 0
                }
            
            async with conn.cursor() as cursor:
                # Build conditions
                conditions = []
                params = []
                
                if identifier:
                    conditions.append("identifier = %s")
                    params.append(identifier)
                
                if window_type:
                    conditions.append("window_type = %s")
                    params.append(window_type)
                
                if start_time:
                    conditions.append("window_start >= %s")
                    params.append(start_time)
                
                if end_time:
                    conditions.append("window_end <= %s")
                    params.append(end_time)
                
                where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
                
                sql = f"""
                    SELECT 
                        SUM(request_count) as total_requests,
                        COUNT(DISTINCT identifier) as unique_identifiers,
                        AVG(request_count) as avg_requests,
                        MAX(request_count) as max_requests,
                        MIN(request_count) as min_requests
                    FROM rate_limit_records
                    {where_clause}
                """
                
                await cursor.execute(sql, params)
                result = await cursor.fetchone()
                
                if result and result[0] is not None:
                    return {
                        "total_requests": int(result[0]) if result[0] else 0,
                        "unique_identifiers": int(result[1]) if result[1] else 0,
                        "average_requests_per_identifier": float(result[2]) if result[2] else 0.0,
                        "max_requests": int(result[3]) if result[3] else 0,
                        "min_requests": int(result[4]) if result[4] else 0
                    }
                else:
                    return {
                        "total_requests": 0,
                        "unique_identifiers": 0,
                        "average_requests_per_identifier": 0.0,
                        "max_requests": 0,
                        "min_requests": 0
                    }
        except Exception:
            return {
                "total_requests": 0,
                "unique_identifiers": 0,
                "average_requests_per_identifier": 0.0,
                "max_requests": 0,
                "min_requests": 0
            }
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

