"""
Test script to verify MySQL storage in auth_service database

This script tests:
1. Connection to auth_service database
2. Table structure
3. Storing a record
4. Querying records
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncmy
from app.settings import get_settings
from datetime import datetime, timedelta


async def test_auth_service_db():
    """Test auth_service database connection and storage"""
    settings = get_settings()
    
    print("=" * 60)
    print("Testing auth_service Database")
    print("=" * 60)
    
    # Override database name to auth_service
    db_name = "auth_service"
    
    print(f"\n1. Testing connection to '{db_name}' database...")
    print(f"   Host: {settings.mysql_host}:{settings.mysql_port}")
    print(f"   User: {settings.mysql_user}")
    
    try:
        conn = await asyncmy.connect(
            host=settings.mysql_host,
            port=settings.mysql_port,
            user=settings.mysql_user,
            password=settings.mysql_password,
            db=db_name
        )
        print(f"   ✓ Connected to '{db_name}' database")
    except Exception as e:
        print(f"   ✗ Connection failed: {e}")
        return
    
    try:
        # Check if table exists
        print(f"\n2. Checking if 'rate_limit_records' table exists...")
        async with conn.cursor() as cursor:
            await cursor.execute("SHOW TABLES LIKE 'rate_limit_records'")
            result = await cursor.fetchone()
            if result:
                print("   ✓ Table 'rate_limit_records' exists")
                
                # Check table structure
                await cursor.execute("DESCRIBE rate_limit_records")
                columns = await cursor.fetchall()
                print("\n   Table structure:")
                for col in columns:
                    print(f"     - {col[0]}: {col[1]}")
            else:
                print("   ✗ Table 'rate_limit_records' does not exist!")
                print("   Please create the table first.")
                conn.close()
                return
        
        # Check current records
        print(f"\n3. Checking existing records...")
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT COUNT(*) FROM rate_limit_records")
            result = await cursor.fetchone()
            count = result[0] if result else 0
            print(f"   Current records: {count}")
            
            if count > 0:
                await cursor.execute(
                    """
                    SELECT identifier, window_type, request_count, route_path, updated_at
                    FROM rate_limit_records
                    ORDER BY updated_at DESC
                    LIMIT 5
                    """
                )
                records = await cursor.fetchall()
                print("\n   Recent records:")
                for record in records:
                    print(f"     - {record[0]} | {record[1]} | Count: {record[2]} | Route: {record[3]}")
        
        # Test storing a record
        print(f"\n4. Testing record storage...")
        identifier = "test_auth_service_user"
        window_type = "minute"
        request_count = 1
        window_start = datetime.utcnow().replace(second=0, microsecond=0)
        window_end = window_start + timedelta(seconds=60)
        route_path = "/auth/login"
        
        async with conn.cursor() as cursor:
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
            print(f"   ✓ Record stored successfully")
        
        # Verify the record
        print(f"\n5. Verifying stored record...")
        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM rate_limit_records WHERE identifier = %s",
                (identifier,)
            )
            records = await cursor.fetchall()
            if records:
                print(f"   ✓ Record found: {len(records)} record(s)")
            else:
                print(f"   ✗ Record not found!")
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        print(f"\nTo use 'auth_service' database, set in .env file:")
        print(f"  MYSQL_DATABASE=auth_service")
        print("\nOr export environment variable:")
        print(f"  export MYSQL_DATABASE=auth_service")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()


if __name__ == "__main__":
    asyncio.run(test_auth_service_db())

