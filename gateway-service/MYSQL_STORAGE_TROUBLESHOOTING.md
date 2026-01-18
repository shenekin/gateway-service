# MySQL Storage Troubleshooting Guide

**Date:** 2025-12-25  
**Issue:** Rate limit records appear in Redis but not in MySQL

## Problem

Rate limit records are being stored in Redis (you can see them with `redis-cli keys *`), but the `rate_limit_records` table in MySQL is empty.

## Root Causes

### 1. Background Tasks Not Completing

When `RATE_LIMIT_MYSQL_ASYNC=true` (default), MySQL storage uses background tasks created with `asyncio.create_task()`. These tasks may not complete if:
- The request finishes very quickly
- The event loop doesn't have time to execute the task
- The application shuts down before tasks complete

### 2. Configuration Issues

- `RATE_LIMIT_MYSQL_ENABLED` might be `false`
- MySQL connection settings might be incorrect
- Table might not exist

### 3. Silent Failures

Errors in background tasks might be silently caught and logged, but not visible if logging level is too high.

## Solutions

### Solution 1: Use Synchronous Storage (Recommended for Reliability)

Set `RATE_LIMIT_MYSQL_ASYNC=false` in your `.env` file:

```bash
RATE_LIMIT_MYSQL_ENABLED=true
RATE_LIMIT_MYSQL_ASYNC=false
```

This ensures MySQL writes complete before the response is sent, guaranteeing records are stored.

**Pros:**
- Guaranteed storage
- No background task issues
- Easier to debug

**Cons:**
- Slightly slower (adds ~5-10ms per request)
- Blocks rate limit check until MySQL write completes

### Solution 2: Check Configuration

Verify your `.env` file has:

```bash
RATE_LIMIT_MYSQL_ENABLED=true
RATE_LIMIT_MYSQL_ASYNC=true  # or false for synchronous
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=gateway_db
MYSQL_USER=root
MYSQL_PASSWORD=your_password
```

### Solution 3: Verify MySQL Connection and Table

Run the diagnostic script:

```bash
python scripts/debug_mysql_storage.py
```

This will:
- Check settings configuration
- Test MySQL connection
- Verify table structure
- Test direct storage
- Test middleware storage

### Solution 4: Check Application Logs

Enable debug logging to see what's happening:

```bash
# In your .env file
LOG_LEVEL=DEBUG
```

Then check logs for:
- `"MySQL rate limit storage enabled: async=True/False"`
- `"Creating background task for MySQL storage"`
- `"MySQL storage task started"`
- `"MySQL storage task completed successfully"`
- `"Failed to store rate limit record in MySQL"`
- `"Error storing rate limit record in MySQL"`

### Solution 5: Verify Table Exists

```bash
# Connect to MySQL
mysql -u root -p gateway_db

# Check table exists
SHOW TABLES LIKE 'rate_limit_records';

# Check table structure
DESCRIBE rate_limit_records;

# Check if there are any records
SELECT COUNT(*) FROM rate_limit_records;
```

If table doesn't exist, run:

```bash
python scripts/database/init_database.py
```

## Diagnostic Steps

### Step 1: Run Diagnostic Script

```bash
python scripts/debug_mysql_storage.py
```

This will identify the issue.

### Step 2: Test Direct Storage

```bash
python scripts/test_mysql_rate_limit_storage.py
```

If this works but middleware doesn't, the issue is with background tasks.

### Step 3: Check Redis Keys

```bash
redis-cli
> keys rate_limit:*
```

Verify rate limiting is working (keys should exist).

### Step 4: Check MySQL

```bash
mysql -u root -p gateway_db
> SELECT * FROM rate_limit_records ORDER BY updated_at DESC LIMIT 10;
```

If empty, storage is not working.

## Quick Fix

**Immediate solution:** Set `RATE_LIMIT_MYSQL_ASYNC=false` in `.env`:

```bash
echo "RATE_LIMIT_MYSQL_ASYNC=false" >> .env
```

Then restart the gateway service. This will use synchronous storage, ensuring records are always stored.

## Why Async Mode Might Not Work

When using `asyncio.create_task()` in async mode:
1. Task is created and scheduled
2. Request continues and response is sent
3. Task may not complete before response is sent
4. If application is under heavy load, tasks might be delayed
5. If application shuts down quickly, tasks might not complete

This is a limitation of "fire and forget" background tasks in async Python.

## Recommended Configuration

For **production** (reliability over speed):
```bash
RATE_LIMIT_MYSQL_ENABLED=true
RATE_LIMIT_MYSQL_ASYNC=false  # Synchronous for reliability
```

For **development** (speed over reliability):
```bash
RATE_LIMIT_MYSQL_ENABLED=true
RATE_LIMIT_MYSQL_ASYNC=true   # Async for speed
```

## Monitoring

After applying the fix, monitor:

1. **Redis keys**: Should continue to work as before
2. **MySQL records**: Should start appearing in `rate_limit_records` table
3. **Application logs**: Should show successful storage messages
4. **Performance**: With sync mode, expect ~5-10ms additional latency per request

## Verification

After fixing, verify with:

```bash
# Make some requests that trigger rate limiting
# Then check MySQL
mysql -u root -p gateway_db -e "SELECT identifier, window_type, request_count, route_path, updated_at FROM rate_limit_records ORDER BY updated_at DESC LIMIT 10;"
```

You should see records appearing.

