"""
Synchronous test script to verify audit log insertion works correctly

This script tests direct insertion (not async) to verify the SQL works.
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
import asyncmy


async def test_direct_insert():
    """Test direct insertion into audit_logs"""
    settings = get_settings()
    
    print("=" * 60)
    print("Direct Audit Log Insertion Test")
    print("=" * 60)
    
    try:
        conn = await asyncmy.connect(
            host=settings.mysql_host,
            port=settings.mysql_port,
            user=settings.mysql_user,
            password=settings.mysql_password,
            db=settings.mysql_database
        )
        print(f"\n✓ Connected to database: {settings.mysql_database}")
        
        async with conn.cursor() as cursor:
            # Test 1: Insert login event
            print("\n1. Inserting login event...")
            sql = """
                INSERT INTO audit_logs 
                (event_type, user_id, ip_address, user_agent, details, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            details = {"method": "password", "success": True}
            details_json = json.dumps(details)
            
            await cursor.execute(
                sql,
                (
                    "login",
                    "test_user_direct",
                    "127.0.0.1",
                    "test-agent/1.0",
                    details_json,
                    datetime.utcnow()
                )
            )
            await conn.commit()
            print("   ✓ Login event inserted")
            
            # Test 2: Insert refresh event
            print("\n2. Inserting refresh event...")
            details = {"token_rotation": True, "old_token_family": "family1"}
            details_json = json.dumps(details)
            
            await cursor.execute(
                sql,
                (
                    "refresh",
                    "test_user_direct",
                    "127.0.0.1",
                    "test-agent/1.0",
                    details_json,
                    datetime.utcnow()
                )
            )
            await conn.commit()
            print("   ✓ Refresh event inserted")
            
            # Test 3: Insert revoke event
            print("\n3. Inserting revoke event...")
            details = {"token": "refresh_token_abc..."}
            details_json = json.dumps(details)
            
            await cursor.execute(
                sql,
                (
                    "revoke",
                    "test_user_direct",
                    "127.0.0.1",
                    "test-agent/1.0",
                    details_json,
                    datetime.utcnow()
                )
            )
            await conn.commit()
            print("   ✓ Revoke event inserted")
            
            # Test 4: Query records
            print("\n4. Querying inserted records...")
            await cursor.execute(
                """
                SELECT event_type, user_id, ip_address, user_agent, details, created_at
                FROM audit_logs
                WHERE user_id = 'test_user_direct'
                ORDER BY created_at DESC
                """
            )
            records = await cursor.fetchall()
            
            if records:
                print(f"   ✓ Found {len(records)} records:")
                for record in records:
                    print(f"     - {record[0]} | {record[1]} | {record[2]} | {record[5]}")
            else:
                print("   ✗ No records found")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("✓ Direct insertion test completed!")
        print("=" * 60)
        print("\nIf direct insertion works but async doesn't:")
        print("1. Check background task completion")
        print("2. Increase wait time in test script")
        print("3. Check application logs for errors")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_direct_insert())

