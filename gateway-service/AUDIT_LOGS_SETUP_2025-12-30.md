# Audit Logs Table Setup and Verification

**Date:** 2025-12-30  
**Purpose:** Create audit_logs table in MySQL and verify data insertion works correctly

## Overview

The audit_logs table stores authentication events (login, refresh, revoke) for audit and compliance purposes. This document describes the table creation and verification process.

## Table Structure

The `audit_logs` table has the following structure:

```sql
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
  COLLATE=utf8mb4_unicode_ci;
```

## Setup Steps

### 1. Create Table

Run the Python script to create the table:

```bash
python scripts/database/create_audit_logs_table.py
```

This script:
- Connects to MySQL using settings from `.env`
- Creates the table if it doesn't exist
- Adds missing columns if table exists
- Creates indexes for better performance

### 2. Verify Table Creation

Check that the table was created:

```bash
mysql -u root -p auth_service -e "DESCRIBE audit_logs;"
```

Or use the test script:

```bash
python scripts/test_audit_log_insert.py
```

### 3. Test Data Insertion

Run the test script to verify data insertion:

```bash
python scripts/test_audit_log_insert.py
```

This will:
- Test database connection
- Verify table structure
- Insert test records for login, refresh, revoke events
- Query and display inserted records

## Database Configuration

The table is created in the database specified by `MYSQL_DATABASE` in `.env`:

```bash
MYSQL_DATABASE=auth_service
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
```

## Event Types

The table stores three types of events:

1. **login**: User login events
   - Stored when user successfully logs in
   - Includes IP address, user agent, and login method details

2. **refresh**: Token refresh events
   - Stored when access token is refreshed
   - Includes token rotation information

3. **revoke**: Token revocation events
   - Stored when refresh token is revoked
   - Includes token information

## Usage in Code

### Logging Login Event

```python
from app.utils.audit_logger import AuditLogger

audit_logger = AuditLogger()
await audit_logger.log_login(
    user_id="user123",
    ip_address="127.0.0.1",
    user_agent="Mozilla/5.0...",
    details={"method": "password", "success": True}
)
```

### Logging Refresh Event

```python
await audit_logger.log_refresh(
    user_id="user123",
    ip_address="127.0.0.1",
    user_agent="Mozilla/5.0...",
    details={"token_rotation": True, "old_token_family": "family1"}
)
```

### Logging Revoke Event

```python
await audit_logger.log_revoke(
    user_id="user123",
    ip_address="127.0.0.1",
    user_agent="Mozilla/5.0...",
    details={"token": "refresh_token_abc..."}
)
```

## Querying Audit Logs

### Query by Event Type

```sql
SELECT * FROM audit_logs 
WHERE event_type = 'login' 
ORDER BY created_at DESC 
LIMIT 10;
```

### Query by User

```sql
SELECT * FROM audit_logs 
WHERE user_id = 'user123' 
ORDER BY created_at DESC;
```

### Query by Date Range

```sql
SELECT * FROM audit_logs 
WHERE created_at >= '2025-12-01' 
  AND created_at < '2025-12-31'
ORDER BY created_at DESC;
```

## Files Created

1. **scripts/database/create_audit_logs_table.py**: Python script to create/update table
2. **scripts/database/create_audit_logs_auth_service.sql**: SQL script for manual execution
3. **scripts/test_audit_log_insert.py**: Test script to verify insertion
4. **scripts/test_audit_log_sync.py**: Direct insertion test (synchronous)

## Verification

After setup, verify the table works:

```bash
# Test async insertion
python scripts/test_audit_log_insert.py

# Test direct insertion
python scripts/test_audit_log_sync.py

# Query records
mysql -u root -p auth_service -e "SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT 10;"
```

## Troubleshooting

### Table Not Created

1. Check MySQL connection settings in `.env`
2. Verify MySQL service is running
3. Check user permissions
4. Run the Python script manually: `python scripts/database/create_audit_logs_table.py`

### Records Not Inserting

1. Check application logs for errors
2. Verify table structure matches code expectations
3. Test direct insertion: `python scripts/test_audit_log_sync.py`
4. Check background tasks are completing (async insertion)

### Connection Errors

1. Verify `MYSQL_DATABASE` is set correctly
2. Check MySQL host and port
3. Verify user credentials
4. Test connection: `mysql -u root -p auth_service`

## Performance Considerations

- Indexes are created on `event_type`, `user_id`, and `created_at` for fast queries
- Composite indexes on `(event_type, created_at)` and `(user_id, created_at)` for time-based queries
- Asynchronous logging prevents blocking request processing
- Background tasks are tracked to ensure completion

## Security

- Audit logs are stored in MySQL for persistence
- IP addresses and user agents are logged for security analysis
- Details field stores JSON for flexible event data
- All authentication events are logged for compliance

