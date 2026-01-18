"""
Test script to verify audit log insertion works correctly

This script tests:
1. Database connection
2. Table structure
3. Insert operations for login, refresh, revoke events
4. Query operations to verify data
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.settings import get_settings
from app.utils.audit_logger import AuditLogger
import asyncmy


async def test_audit_log_insertion():
    """Test audit log insertion"""
    settings = get_settings()
    audit_logger = AuditLogger()
    
    print("=" * 60)
    print("Audit Log Insertion Test")
    print("=" * 60)
    
    # Test 1: Check database connection
    print("\n1. Testing database connection...")
    conn = await audit_logger._get_connection()
    if not conn:
        print("   ✗ Database connection failed!")
        print(f"   Check settings: {settings.mysql_host}:{settings.mysql_port}")
        print(f"   Database: {settings.mysql_database}")
        return False
    print(f"   ✓ Connected to database: {settings.mysql_database}")
    
    # Test 2: Check table exists
    print("\n2. Checking audit_logs table...")
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("SHOW TABLES LIKE 'audit_logs'")
            result = await cursor.fetchone()
            if not result:
                print("   ✗ Table 'audit_logs' does not exist!")
                print("   Run: mysql -u root -p < scripts/database/create_audit_logs_table.sql")
                conn.close()
                return False
            
            print("   ✓ Table 'audit_logs' exists")
            
            # Check table structure
            await cursor.execute("DESCRIBE audit_logs")
            columns = await cursor.fetchall()
            print("\n   Table structure:")
            required_columns = ['event_type', 'user_id', 'ip_address', 'user_agent', 'details']
            for col in columns:
                col_name = col[0]
                col_type = col[1]
                print(f"     - {col_name}: {col_type}")
                if col_name in required_columns:
                    required_columns.remove(col_name)
            
            if required_columns:
                print(f"\n   ⚠ Missing columns: {', '.join(required_columns)}")
                print("   Run: mysql -u root -p < scripts/database/create_audit_logs_table.sql")
    except Exception as e:
        print(f"   ✗ Error checking table: {e}")
        conn.close()
        return False
    
    # Test 3: Test login event insertion
    print("\n3. Testing login event insertion...")
    try:
        await audit_logger.log_login(
            user_id="test_user_123",
            ip_address="127.0.0.1",
            user_agent="test-agent/1.0",
            details={"method": "password", "success": True}
        )
        print("   ✓ Login event logged (async)")
        
        # Wait for background task to complete
        await asyncio.sleep(2)
        if audit_logger._background_tasks:
            await asyncio.gather(*audit_logger._background_tasks, return_exceptions=True)
            await asyncio.sleep(0.5)
        
        # Verify insertion
        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM audit_logs WHERE user_id = %s AND event_type = 'login' ORDER BY created_at DESC LIMIT 1",
                ("test_user_123",)
            )
            record = await cursor.fetchone()
            if record:
                print("   ✓ Login record found in database")
            else:
                print("   ✗ Login record not found in database")
    except Exception as e:
        print(f"   ✗ Error inserting login event: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Test refresh event insertion
    print("\n4. Testing refresh event insertion...")
    try:
        await audit_logger.log_refresh(
            user_id="test_user_123",
            ip_address="127.0.0.1",
            user_agent="test-agent/1.0",
            details={"token_rotation": True, "old_token_family": "family1"}
        )
        print("   ✓ Refresh event logged (async)")
        
        # Wait for background task to complete
        await asyncio.sleep(2)
        if audit_logger._background_tasks:
            await asyncio.gather(*audit_logger._background_tasks, return_exceptions=True)
            await asyncio.sleep(0.5)
        
        # Verify insertion
        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM audit_logs WHERE user_id = %s AND event_type = 'refresh' ORDER BY created_at DESC LIMIT 1",
                ("test_user_123",)
            )
            record = await cursor.fetchone()
            if record:
                print("   ✓ Refresh record found in database")
            else:
                print("   ✗ Refresh record not found in database")
    except Exception as e:
        print(f"   ✗ Error inserting refresh event: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 5: Test revoke event insertion
    print("\n5. Testing revoke event insertion...")
    try:
        await audit_logger.log_revoke(
            user_id="test_user_123",
            ip_address="127.0.0.1",
            user_agent="test-agent/1.0",
            details={"token": "refresh_token_abc..."}
        )
        print("   ✓ Revoke event logged (async)")
        
        # Wait for background task to complete
        await asyncio.sleep(2)
        if audit_logger._background_tasks:
            await asyncio.gather(*audit_logger._background_tasks, return_exceptions=True)
            await asyncio.sleep(0.5)
        
        # Verify insertion
        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM audit_logs WHERE user_id = %s AND event_type = 'revoke' ORDER BY created_at DESC LIMIT 1",
                ("test_user_123",)
            )
            record = await cursor.fetchone()
            if record:
                print("   ✓ Revoke record found in database")
            else:
                print("   ✗ Revoke record not found in database")
    except Exception as e:
        print(f"   ✗ Error inserting revoke event: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 6: Query all test records
    print("\n6. Querying all test records...")
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(
                """
                SELECT event_type, user_id, ip_address, user_agent, details, created_at
                FROM audit_logs
                WHERE user_id = 'test_user_123'
                ORDER BY created_at DESC
                LIMIT 10
                """
            )
            records = await cursor.fetchall()
            
            if records:
                print(f"   ✓ Found {len(records)} test records:")
                for record in records:
                    print(f"     - {record[0]} | {record[1]} | {record[2]} | {record[5]}")
            else:
                print("   ⚠ No test records found")
    except Exception as e:
        print(f"   ✗ Error querying records: {e}")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)
    print("\nIf records are not appearing:")
    print("1. Check MySQL connection settings in .env")
    print("2. Verify table exists: mysql -u root -p -e 'USE auth_service; DESCRIBE audit_logs;'")
    print("3. Check application logs for errors")
    print("4. Ensure MYSQL_DATABASE is set correctly in .env")


if __name__ == "__main__":
    asyncio.run(test_audit_log_insertion())

