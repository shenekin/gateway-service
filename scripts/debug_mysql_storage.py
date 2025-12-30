"""
Debug script to check why MySQL storage is not working

This script checks:
1. Settings configuration
2. MySQL connection
3. Table structure
4. Actual storage attempt
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.settings import get_settings
from app.utils.rate_limit_storage import RateLimitStorage
from app.middleware.rate_limit import RateLimitMiddleware
from fastapi import FastAPI
from datetime import datetime, timedelta
import logging

# Configure logging to see all debug messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def check_settings():
    """Check if settings are configured correctly"""
    print("\n" + "=" * 60)
    print("1. Checking Settings")
    print("=" * 60)
    settings = get_settings()
    
    print(f"  rate_limit_enabled: {settings.rate_limit_enabled}")
    print(f"  rate_limit_mysql_enabled: {settings.rate_limit_mysql_enabled}")
    print(f"  rate_limit_mysql_async: {settings.rate_limit_mysql_async}")
    print(f"  mysql_host: {settings.mysql_host}")
    print(f"  mysql_port: {settings.mysql_port}")
    print(f"  mysql_database: {settings.mysql_database}")
    print(f"  mysql_user: {settings.mysql_user}")
    
    if not settings.rate_limit_mysql_enabled:
        print("\n  ✗ MySQL storage is DISABLED in settings!")
        print("  Set RATE_LIMIT_MYSQL_ENABLED=true in .env file")
        return False
    
    print("  ✓ Settings look correct")
    return True


async def check_mysql_connection():
    """Check MySQL connection"""
    print("\n" + "=" * 60)
    print("2. Checking MySQL Connection")
    print("=" * 60)
    
    storage = RateLimitStorage()
    conn = await storage._get_connection()
    
    if not conn:
        print("  ✗ MySQL connection failed!")
        return False
    
    print("  ✓ MySQL connection successful")
    
    # Check table exists
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("SHOW TABLES LIKE 'rate_limit_records'")
            result = await cursor.fetchone()
            if result:
                print("  ✓ Table 'rate_limit_records' exists")
                
                # Check table structure
                await cursor.execute("DESCRIBE rate_limit_records")
                columns = await cursor.fetchall()
                print("\n  Table structure:")
                for col in columns:
                    print(f"    - {col[0]}: {col[1]}")
            else:
                print("  ✗ Table 'rate_limit_records' does not exist!")
                print("  Run: python scripts/database/init_database.py")
                conn.close()
                return False
    except Exception as e:
        print(f"  ✗ Error checking table: {e}")
        conn.close()
        return False
    finally:
        conn.close()
    
    return True


async def test_direct_storage():
    """Test direct storage (bypassing middleware)"""
    print("\n" + "=" * 60)
    print("3. Testing Direct MySQL Storage")
    print("=" * 60)
    
    storage = RateLimitStorage()
    
    identifier = "test_debug_user"
    window_type = "minute"
    request_count = 1
    window_start = datetime.utcnow().replace(second=0, microsecond=0)
    window_end = window_start + timedelta(seconds=60)
    route_path = "/auth/login"
    
    print(f"  Attempting to store: identifier={identifier}, window={window_type}, count={request_count}")
    
    result = await storage.store_rate_limit_record(
        identifier=identifier,
        window_type=window_type,
        request_count=request_count,
        window_start=window_start,
        window_end=window_end,
        route_path=route_path
    )
    
    if result:
        print("  ✓ Direct storage successful")
        
        # Verify it was stored
        conn = await storage._get_connection()
        if conn:
            try:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        "SELECT * FROM rate_limit_records WHERE identifier = %s",
                        (identifier,)
                    )
                    records = await cursor.fetchall()
                    if records:
                        print(f"  ✓ Record found in database: {len(records)} record(s)")
                    else:
                        print("  ✗ Record not found in database after storage!")
            except Exception as e:
                print(f"  ✗ Error querying: {e}")
            finally:
                conn.close()
    else:
        print("  ✗ Direct storage failed")
    
    return result


async def test_middleware_storage():
    """Test storage through middleware"""
    print("\n" + "=" * 60)
    print("4. Testing Middleware Storage")
    print("=" * 60)
    
    app = FastAPI()
    middleware = RateLimitMiddleware(app)
    
    print(f"  MySQL storage initialized: {middleware.mysql_storage is not None}")
    print(f"  Settings enabled: {middleware.settings.rate_limit_mysql_enabled}")
    print(f"  Settings async: {middleware.settings.rate_limit_mysql_async}")
    
    if not middleware.mysql_storage:
        print("  ✗ MySQL storage not initialized in middleware!")
        return False
    
    # Test the async storage method
    identifier = "test_middleware_user"
    window = "minute"
    route_path = "/auth/login"
    request_count = 1
    window_seconds = 60
    
    print(f"  Calling _store_rate_limit_record_async: identifier={identifier}")
    
    try:
        await middleware._store_rate_limit_record_async(
            identifier=identifier,
            window=window,
            route_path=route_path,
            request_count=request_count,
            window_seconds=window_seconds
        )
        print("  ✓ _store_rate_limit_record_async called successfully")
        
        # Wait a bit for async task to complete
        if middleware.settings.rate_limit_mysql_async:
            print("  Waiting 2 seconds for background task to complete...")
            await asyncio.sleep(2)
            
            # Check if task completed
            print(f"  Active background tasks: {len(middleware._background_tasks)}")
        
        # Verify it was stored
        storage = RateLimitStorage()
        conn = await storage._get_connection()
        if conn:
            try:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        "SELECT * FROM rate_limit_records WHERE identifier = %s",
                        (identifier,)
                    )
                    records = await cursor.fetchall()
                    if records:
                        print(f"  ✓ Record found in database: {len(records)} record(s)")
                    else:
                        print("  ✗ Record not found in database after middleware storage!")
                        print("  This suggests the background task may not be completing")
            except Exception as e:
                print(f"  ✗ Error querying: {e}")
            finally:
                conn.close()
        
    except Exception as e:
        print(f"  ✗ Error in middleware storage: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


async def main():
    """Run all diagnostic checks"""
    print("=" * 60)
    print("MySQL Rate Limit Storage Diagnostic")
    print("=" * 60)
    
    # Check settings
    settings_ok = await check_settings()
    if not settings_ok:
        print("\n✗ Settings check failed. Please fix configuration.")
        return
    
    # Check MySQL connection
    connection_ok = await check_mysql_connection()
    if not connection_ok:
        print("\n✗ MySQL connection check failed. Please fix connection.")
        return
    
    # Test direct storage
    direct_ok = await test_direct_storage()
    
    # Test middleware storage
    middleware_ok = await test_middleware_storage()
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"  Settings: {'✓' if settings_ok else '✗'}")
    print(f"  MySQL Connection: {'✓' if connection_ok else '✗'}")
    print(f"  Direct Storage: {'✓' if direct_ok else '✗'}")
    print(f"  Middleware Storage: {'✓' if middleware_ok else '✗'}")
    
    if direct_ok and not middleware_ok:
        print("\n⚠ Direct storage works but middleware storage doesn't.")
        print("  This suggests the background task is not completing.")
        print("  Try setting RATE_LIMIT_MYSQL_ASYNC=false to use synchronous storage.")
    elif not direct_ok:
        print("\n⚠ Direct storage failed. Check MySQL connection and table structure.")
    elif middleware_ok:
        print("\n✓ All checks passed! MySQL storage should be working.")


if __name__ == "__main__":
    asyncio.run(main())

