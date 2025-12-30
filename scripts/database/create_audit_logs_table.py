"""
Python script to create audit_logs table in MySQL

This script:
1. Connects to MySQL database
2. Creates audit_logs table if it doesn't exist
3. Adds missing columns if table exists but is missing columns
4. Creates indexes for better performance
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.settings import get_settings
import asyncmy


async def create_audit_logs_table():
    """Create audit_logs table"""
    settings = get_settings()
    
    print("=" * 60)
    print("Creating audit_logs Table")
    print("=" * 60)
    print(f"\nDatabase: {settings.mysql_database}")
    print(f"Host: {settings.mysql_host}:{settings.mysql_port}")
    print(f"User: {settings.mysql_user}")
    
    try:
        # Connect to MySQL
        conn = await asyncmy.connect(
            host=settings.mysql_host,
            port=settings.mysql_port,
            user=settings.mysql_user,
            password=settings.mysql_password,
            db=settings.mysql_database
        )
        print("\n✓ Connected to MySQL")
        
        async with conn.cursor() as cursor:
            # Check if table exists
            await cursor.execute("SHOW TABLES LIKE 'audit_logs'")
            table_exists = await cursor.fetchone()
            
            if table_exists:
                print("✓ Table 'audit_logs' already exists")
                
                # Check table structure
                await cursor.execute("DESCRIBE audit_logs")
                columns = await cursor.fetchall()
                column_names = [col[0] for col in columns]
                
                required_columns = {
                    'event_type': "VARCHAR(50) NOT NULL COMMENT 'Event type (login, refresh, revoke)'",
                    'ip_address': "VARCHAR(50) COMMENT 'Client IP address'",
                    'user_agent': "VARCHAR(500) COMMENT 'User agent string'",
                    'details': "TEXT COMMENT 'Additional event details (JSON)'"
                }
                
                # Add missing columns
                for col_name, col_def in required_columns.items():
                    if col_name not in column_names:
                        print(f"  Adding missing column: {col_name}")
                        try:
                            if col_name == 'event_type':
                                # event_type should be after id
                                await cursor.execute(
                                    f"ALTER TABLE audit_logs ADD COLUMN {col_name} {col_def} AFTER id"
                                )
                            else:
                                await cursor.execute(
                                    f"ALTER TABLE audit_logs ADD COLUMN {col_name} {col_def}"
                                )
                            print(f"  ✓ Added column: {col_name}")
                        except Exception as e:
                            print(f"  ⚠ Error adding column {col_name}: {e}")
                
                await conn.commit()
            else:
                # Create table
                print("\nCreating audit_logs table...")
                create_table_sql = """
                    CREATE TABLE audit_logs (
                        id BIGINT AUTO_INCREMENT PRIMARY KEY,
                        event_type VARCHAR(50) NOT NULL COMMENT 'Event type (login, refresh, revoke)',
                        user_id VARCHAR(100) NOT NULL COMMENT 'User identifier',
                        ip_address VARCHAR(50) COMMENT 'Client IP address',
                        user_agent VARCHAR(500) COMMENT 'User agent string',
                        details TEXT COMMENT 'Additional event details (JSON)',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
                        
                        INDEX idx_event_type (event_type),
                        INDEX idx_user_id (user_id),
                        INDEX idx_created_at (created_at),
                        INDEX idx_event_type_created_at (event_type, created_at),
                        INDEX idx_user_id_created_at (user_id, created_at)
                    ) ENGINE=InnoDB 
                      DEFAULT CHARSET=utf8mb4 
                      COLLATE=utf8mb4_unicode_ci 
                      COMMENT='Audit logs for authentication events (login, refresh, revoke)'
                """
                
                await cursor.execute(create_table_sql)
                await conn.commit()
                print("✓ Table 'audit_logs' created successfully")
            
            # Create indexes if they don't exist
            print("\nCreating indexes...")
            indexes = [
                ("idx_event_type", "event_type"),
                ("idx_user_id", "user_id"),
                ("idx_created_at", "created_at"),
                ("idx_event_type_created_at", "event_type, created_at"),
                ("idx_user_id_created_at", "user_id, created_at")
            ]
            
            for index_name, columns in indexes:
                try:
                    await cursor.execute(
                        f"CREATE INDEX IF NOT EXISTS {index_name} ON audit_logs({columns})"
                    )
                    print(f"  ✓ Index {index_name} created or already exists")
                except Exception as e:
                    # MySQL doesn't support IF NOT EXISTS for indexes, check if exists
                    await cursor.execute(f"SHOW INDEX FROM audit_logs WHERE Key_name = '{index_name}'")
                    if not await cursor.fetchone():
                        try:
                            await cursor.execute(f"CREATE INDEX {index_name} ON audit_logs({columns})")
                            print(f"  ✓ Index {index_name} created")
                        except Exception as e2:
                            print(f"  ⚠ Index {index_name} may already exist: {e2}")
            
            await conn.commit()
            
            # Show final table structure
            print("\n" + "=" * 60)
            print("Final Table Structure:")
            print("=" * 60)
            await cursor.execute("DESCRIBE audit_logs")
            columns = await cursor.fetchall()
            print("\nColumns:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]} {col[2] if col[2] == 'NO' else 'NULL'}")
            
            # Show indexes
            print("\nIndexes:")
            await cursor.execute("SHOW INDEX FROM audit_logs")
            indexes = await cursor.fetchall()
            index_names = set()
            for idx in indexes:
                index_names.add(idx[2])  # Key_name
            for idx_name in sorted(index_names):
                print(f"  - {idx_name}")
        
        conn.close()
        print("\n" + "=" * 60)
        print("✓ Table setup completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(create_audit_logs_table())

