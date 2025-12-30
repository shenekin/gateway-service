# Body Handling Fix for 422 Validation Error

## Problem

Getting `422 Unprocessable Entity` error with message:
```json
{
    "status": "error",
    "error_code": "VALIDATION_ERROR",
    "message": "Input should be a valid dictionary or object to extract fields from",
    "details": {
        "errors": [
            {
                "field": "body",
                "error_code": "VALIDATION_ERROR",
                "message": "Input should be a valid dictionary or object to extract fields from",
                "path": "body"
            }
        ]
    }
}
```

## Root Cause

The issue occurs because:
1. **Request body is consumed**: When we read `request.body()` in the rate limiting middleware, the body stream is consumed
2. **Body not properly preserved**: The body needs to be stored and reused for forwarding to backend services
3. **Timing issue**: Body reading happens at the wrong time in the request lifecycle

## Solution

### Changes Made

1. **Moved body reading to middleware dispatch**:
   - Body is now read in `RateLimitMiddleware.dispatch()` method
   - This happens before the route handler runs
   - Body is stored in `request.state._body` for reuse

2. **Improved body preservation**:
   - Body is stored as bytes in `request.state._body`
   - Route handler checks for stored body before reading
   - Body is properly forwarded to backend services

3. **Better error handling**:
   - Added try-catch blocks around body reading
   - Handle cases where body might be empty or None
   - Only read body for methods that typically have bodies

### Code Flow

1. **Request arrives** → `RateLimitMiddleware.dispatch()` is called
2. **For login endpoints** → Body is read and stored in `request.state._body`
3. **Login identifier extracted** → Username/email extracted from body
4. **Route handler runs** → Checks for stored body, uses it if available
5. **Request forwarded** → Body is forwarded to backend service as bytes

### Key Changes

#### `app/middleware/rate_limit.py`

- **Line 272-295**: Enhanced `dispatch()` method to read body for login endpoints
- **Line 189-201**: Improved body reading with better error handling
- **Line 212-240**: Simplified `check_request_rate_limit()` - body reading moved to middleware

#### `app/main.py`

- **Line 229-251**: Improved body handling in route handler
- **Line 253-270**: Simplified body forwarding logic

## Testing

To verify the fix works:

1. **Test login endpoint**:
   ```bash
   curl -X POST http://localhost:8001/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "password": "testpass"}'
   ```

2. **Test other POST endpoint**:
   ```bash
   curl -X POST http://localhost:8001/projects \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <token>" \
     -d '{"name": "test project"}'
   ```

3. **Check logs**:
   ```bash
   tail -f logs/request.log
   tail -f logs/error.log
   ```

## If Error Persists

If you're still getting 422 errors:

1. **Check if error is from backend**: The 422 might be coming from the backend service, not the gateway
   - Check backend service logs
   - Verify backend service is expecting the correct format

2. **Verify request format**:
   - Ensure `Content-Type: application/json` header is set
   - Ensure request body is valid JSON
   - Check that body is not empty for POST/PUT requests

3. **Enable debug logging**:
   ```bash
   python run.py --log-level debug
   ```

4. **Check body preservation**:
   - Add logging to see if body is being stored correctly
   - Verify body is being forwarded correctly

## Verification

The fix ensures:
- ✅ Body is read only once (in middleware for login endpoints)
- ✅ Body is properly stored in `request.state._body`
- ✅ Body is reused for forwarding to backend services
- ✅ Body is forwarded as bytes (not dict or string)
- ✅ Empty bodies are handled gracefully

## Notes

- Body reading only happens for login/register endpoints in middleware
- For other endpoints, body is read in route handler if needed
- Body is always stored as bytes, never as dict or string
- Backend service receives body exactly as client sent it

