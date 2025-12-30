"""
Quick script to check if MySQL records are being stored

This script queries the rate_limit_records table to see if any records exist.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.utils.rate_limit_storage import RateLimitStorage


async def check_records():
    """Check if any records exist in MySQL"""
    storage = RateLimitStorage()
    
    conn = await storage._get_connection()
    if not conn:
        print("✗ Cannot connect to MySQL")
        return
    
    try:
        async with conn.cursor() as cursor:
            # Get total count
            await cursor.execute("SELECT COUNT(*) FROM rate_limit_records")
            result = await cursor.fetchone()
            count = result[0] if result else 0
            
            print(f"Total records in rate_limit_records: {count}")
            
            if count > 0:
                # Get recent records
                await cursor.execute(
                    """
                    SELECT identifier, window_type, request_count, route_path, 
                           window_start, window_end, created_at, updated_at
                    FROM rate_limit_records
                    ORDER BY updated_at DESC
                    LIMIT 10
                    """
                )
                records = await cursor.fetchall()
                
                print("\nRecent records:")
                for record in records:
                    print(f"  - {record[0]} | {record[1]} | Count: {record[2]} | Route: {record[3]} | Updated: {record[7]}")
            else:
                print("\n⚠ No records found in MySQL!")
                print("  This means MySQL storage is not working.")
                print("  Check:")
                print("  1. RATE_LIMIT_MYSQL_ENABLED=true in .env")
                print("  2. Application logs for errors")
                print("  3. Try setting RATE_LIMIT_MYSQL_ASYNC=false")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()


if __name__ == "__main__":
    asyncio.run(check_records())

