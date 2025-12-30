"""
Test script to verify MySQL rate limit storage is working

This script tests the MySQL storage functionality independently
to help diagnose why records might not be appearing in the database.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.settings import get_settings
from app.utils.rate_limit_storage import RateLimitStorage
from datetime import datetime, timedelta


async def test_mysql_connection():
    """Test MySQL connection"""
    print("Testing MySQL connection...")
    settings = get_settings()
    storage = RateLimitStorage()
    
    conn = await storage._get_connection()
    if conn:
        print("✓ MySQL connection successful")
        conn.close()
        return True
    else:
        print("✗ MySQL connection failed")
        return False


async def test_store_record():
    """Test storing a rate limit record"""
    print("\nTesting rate limit record storage...")
    settings = get_settings()
    storage = RateLimitStorage()
    
    # Test data
    identifier = "test_user_123"
    window_type = "minute"
    request_count = 5
    window_start = datetime.utcnow().replace(second=0, microsecond=0)
    window_end = window_start + timedelta(seconds=60)
    route_path = "/api/test"
    
    result = await storage.store_rate_limit_record(
        identifier=identifier,
        window_type=window_type,
        request_count=request_count,
        window_start=window_start,
        window_end=window_end,
        route_path=route_path
    )
    
    if result:
        print(f"✓ Successfully stored rate limit record")
        print(f"  - Identifier: {identifier}")
        print(f"  - Window: {window_type}")
        print(f"  - Count: {request_count}")
        print(f"  - Route: {route_path}")
        return True
    else:
        print("✗ Failed to store rate limit record")
        return False


async def test_query_record():
    """Test querying a rate limit record from MySQL"""
    print("\nTesting rate limit record query...")
    settings = get_settings()
    storage = RateLimitStorage()
    
    conn = await storage._get_connection()
    if not conn:
        print("✗ Cannot query - MySQL connection failed")
        return False
    
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT COUNT(*) as count FROM rate_limit_records"
            )
            result = await cursor.fetchone()
            count = result[0] if result else 0
            print(f"✓ Total records in rate_limit_records table: {count}")
            
            # Get recent records
            await cursor.execute(
                """
                SELECT identifier, window_type, request_count, route_path, 
                       window_start, window_end, created_at, updated_at
                FROM rate_limit_records
                ORDER BY updated_at DESC
                LIMIT 5
                """
            )
            records = await cursor.fetchall()
            
            if records:
                print("\nRecent records:")
                for record in records:
                    print(f"  - {record[0]} | {record[1]} | Count: {record[2]} | Route: {record[3]}")
            else:
                print("  No records found")
            
            return True
    except Exception as e:
        print(f"✗ Error querying records: {e}")
        return False
    finally:
        conn.close()


async def main():
    """Run all tests"""
    print("=" * 60)
    print("MySQL Rate Limit Storage Test")
    print("=" * 60)
    
    # Check settings
    settings = get_settings()
    print(f"\nConfiguration:")
    print(f"  - MySQL Host: {settings.mysql_host}:{settings.mysql_port}")
    print(f"  - MySQL Database: {settings.mysql_database}")
    print(f"  - MySQL User: {settings.mysql_user}")
    print(f"  - Rate Limit MySQL Enabled: {settings.rate_limit_mysql_enabled}")
    print(f"  - Rate Limit MySQL Async: {settings.rate_limit_mysql_async}")
    
    # Run tests
    connection_ok = await test_mysql_connection()
    if not connection_ok:
        print("\n✗ Cannot proceed - MySQL connection failed")
        print("  Please check:")
        print("  1. MySQL is running")
        print("  2. Database and tables exist (run scripts/database/init_database.py)")
        print("  3. Connection settings in .env are correct")
        return
    
    query_ok = await test_query_record()
    store_ok = await test_store_record()
    
    if store_ok:
        # Query again to verify the new record
        print("\n" + "=" * 60)
        await test_query_record()
    
    print("\n" + "=" * 60)
    if connection_ok and store_ok:
        print("✓ All tests passed")
    else:
        print("✗ Some tests failed")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

