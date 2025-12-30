"""
Quick script to check records in auth_service database
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncmy
from app.settings import get_settings


async def check_records():
    """Check records in auth_service database"""
    settings = get_settings()
    db_name = "auth_service"
    
    try:
        conn = await asyncmy.connect(
            host=settings.mysql_host,
            port=settings.mysql_port,
            user=settings.mysql_user,
            password=settings.mysql_password,
            db=db_name
        )
        
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT COUNT(*) FROM rate_limit_records")
            result = await cursor.fetchone()
            count = result[0] if result else 0
            
            print(f"Total records in auth_service.rate_limit_records: {count}")
            
            if count > 0:
                await cursor.execute(
                    """
                    SELECT identifier, window_type, request_count, route_path, updated_at
                    FROM rate_limit_records
                    ORDER BY updated_at DESC
                    LIMIT 10
                    """
                )
                records = await cursor.fetchall()
                
                print("\nRecent records:")
                for record in records:
                    print(f"  - {record[0]} | {record[1]} | Count: {record[2]} | Route: {record[3]} | Updated: {record[4]}")
            else:
                print("\n⚠ No records found!")
                print("  Make sure:")
                print("  1. MYSQL_DATABASE=auth_service is set in .env")
                print("  2. Gateway service is restarted")
                print("  3. Rate limiting is enabled")
        
        conn.close()
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(check_records())

