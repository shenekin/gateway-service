# MySQL Rate Limit Storage Fix

**Date:** 2025-12-25  
**Issue:** MySQL `rate_limit_records` table is empty, records only appear in Redis  
**Update:** 2025-12-25 - Fixed MySQL deprecation warning for `VALUES()` function

## Problem Analysis

The MySQL storage for rate limit records was not working because:

1. **Background Task Not Tracked**: When `rate_limit_mysql_async` is enabled, `asyncio.create_task()` creates a background task, but the task reference was not being tracked, potentially leading to garbage collection before completion.

2. **Silent Failures**: Errors in the background task were being silently ignored, making it difficult to diagnose why records weren't being stored.

3. **Missing Error Logging**: The MySQL storage methods lacked proper error logging, making it impossible to see what was failing.

## Solution

### 1. Added Background Task Tracking

**File:** `app/middleware/rate_limit.py`

- **Line 34-36**: Initialize `_background_tasks` set to track async MySQL storage tasks
- **Line 228-232**: Store task reference in set and add done callback to prevent memory leaks
- **Reason**: Ensures background tasks complete even if request finishes quickly

```python
# Initialize background tasks set
self._background_tasks: set = set()

# In _store_rate_limit_record_async:
task = asyncio.create_task(store_record_with_error_handling())
self._background_tasks.add(task)
task.add_done_callback(self._background_tasks.discard)
```

### 2. Enhanced Error Handling and Logging

**File:** `app/middleware/rate_limit.py`

- **Line 189-219**: Wrapped MySQL storage in `store_record_with_error_handling()` function with comprehensive error handling
- **Reason**: Ensures errors are logged and don't fail silently

**File:** `app/utils/rate_limit_storage.py`

- **Line 90-94**: Added warning log when MySQL connection fails
- **Line 130-136**: Added debug log when record is successfully stored
- **Line 140-147**: Enhanced error logging with full exception traceback
- **Line 49-53**: Added debug log for connection errors

### 4. Added Test Script

**File:** `scripts/test_mysql_rate_limit_storage.py`

Created a diagnostic script to test MySQL storage independently:
- Tests MySQL connection
- Tests storing a rate limit record
- Tests querying records from database
- Helps verify MySQL storage is working correctly

## Testing

### Run Diagnostic Script

```bash
python scripts/test_mysql_rate_limit_storage.py
```

This will:
1. Test MySQL connection
2. Query existing records
3. Store a test record
4. Query again to verify the record was stored

### Verify in Production

1. **Check Logs**: Look for MySQL storage logs:
   - Success: `"Stored rate limit record: identifier=..., window=..., count=..."`
   - Failure: `"Error storing rate limit record in MySQL: ..."`
   - Connection issues: `"MySQL connection failed for rate limit storage"`

2. **Check Database**: Query the `rate_limit_records` table:
   ```sql
   SELECT * FROM rate_limit_records ORDER BY updated_at DESC LIMIT 10;
   ```

3. **Monitor Background Tasks**: The tasks are now tracked in `_background_tasks` set, ensuring they complete.

## Configuration

Ensure these settings are correct in your `.env` file:

```env
# Enable MySQL storage
RATE_LIMIT_MYSQL_ENABLED=true

# Use async storage (recommended for production)
RATE_LIMIT_MYSQL_ASYNC=true

# MySQL connection settings
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=gateway_db
```

## Troubleshooting

### Records Still Not Appearing

1. **Check MySQL Connection**:
   ```bash
   python scripts/test_mysql_rate_limit_storage.py
   ```

2. **Check Logs**: Look for error messages in application logs

3. **Verify Table Exists**:
   ```sql
   SHOW TABLES LIKE 'rate_limit_records';
   DESCRIBE rate_limit_records;
   ```

4. **Check Settings**: Verify `RATE_LIMIT_MYSQL_ENABLED=true` in your `.env` file

5. **Disable Async Mode**: Temporarily set `RATE_LIMIT_MYSQL_ASYNC=false` to use synchronous storage (for debugging)

### Common Issues

- **Connection Failed**: Check MySQL is running and connection settings are correct
- **Table Missing**: Run `scripts/database/init_database.py` to create tables
- **Permission Issues**: Ensure MySQL user has INSERT/UPDATE permissions
- **Silent Failures**: Check application logs for error messages (now properly logged)

## Changes Summary

### Files Modified

1. **app/middleware/rate_limit.py**:
   - Added `asyncio` import
   - Added `_background_tasks` set initialization
   - Enhanced `_store_rate_limit_record_async()` with error handling wrapper
   - Added task tracking to prevent garbage collection

2. **app/utils/rate_limit_storage.py**:
   - Added logging for connection failures
   - Added debug logging for successful storage
   - Enhanced error logging with full traceback
   - **Fixed MySQL deprecation warning**: Updated SQL to use alias syntax (`AS new`) instead of deprecated `VALUES()` function

### Files Created

1. **scripts/test_mysql_rate_limit_storage.py**:
   - Diagnostic script to test MySQL storage independently

## Next Steps

1. Run the diagnostic script to verify MySQL storage is working
2. Monitor application logs for any errors
3. Check the database to confirm records are being stored
4. If issues persist, temporarily disable async mode (`RATE_LIMIT_MYSQL_ASYNC=false`) to use synchronous storage

