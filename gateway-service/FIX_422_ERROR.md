# Fix for 422 Unprocessable Entity Error

## Problem

Getting `422 Unprocessable Entity` error when making requests to the gateway.

## Root Cause

The 422 error can occur for several reasons:

1. **Request Body Consumption**: The request body is being read during rate limiting, which can cause issues if:
   - The body stream is consumed before it can be forwarded
   - FastAPI tries to parse the body but it's already consumed
   - The body isn't properly preserved for forwarding

2. **Backend Service Error**: The 422 might be coming FROM the backend service, not the gateway itself

3. **Request Validation**: FastAPI might be trying to validate the request body

## Solution

The code has been updated to:

1. **Only read body for login endpoints**: The body is only read when extracting login identifiers for `/auth/login` and `/auth/register` endpoints
2. **Preserve body for forwarding**: The body is stored in `request.state._body` and reused when forwarding to backend services
3. **Better error handling**: Added try-catch blocks to handle body reading failures gracefully

## Code Changes

### `app/middleware/rate_limit.py`

- Only extracts login identifier for login/register endpoints
- Stores body in `request.state._body` for reuse
- Handles body reading errors gracefully

### `app/main.py`

- Checks if body was already read before reading again
- Uses stored body if available
- Handles body reading errors

## Testing

To test if the fix works:

1. **Test login endpoint:**
   ```bash
   curl -X POST http://localhost:8001/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "password": "testpass"}'
   ```

2. **Test other endpoints:**
   ```bash
   curl -X POST http://localhost:8001/projects \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <token>" \
     -d '{"name": "test project"}'
   ```

## If 422 Persists

If you're still getting 422 errors:

1. **Check if it's from backend**: The 422 might be coming from the backend service, not the gateway
   - Check the response headers for `X-Request-Id` to trace the request
   - Check backend service logs

2. **Check request format**: Ensure the request body is valid JSON
   ```bash
   # Validate JSON
   echo '{"test": "data"}' | python -m json.tool
   ```

3. **Check Content-Type**: Ensure `Content-Type: application/json` header is set

4. **Enable debug logging**:
   ```bash
   python run.py --log-level debug
   ```

5. **Check gateway logs**:
   ```bash
   tail -f logs/error.log
   tail -f logs/request.log
   ```

## Common Causes of 422

1. **Invalid JSON**: Request body is not valid JSON
2. **Missing Content-Type**: `Content-Type: application/json` header missing
3. **Empty body for POST**: POST request with no body when body is required
4. **Backend validation**: Backend service rejecting the request
5. **Body consumed**: Request body was read but not preserved (now fixed)

## Verification

The fix ensures:
- ✅ Body is only read when necessary (login endpoints)
- ✅ Body is preserved for forwarding to backend services
- ✅ Errors are handled gracefully
- ✅ Non-login endpoints don't consume body unnecessarily

