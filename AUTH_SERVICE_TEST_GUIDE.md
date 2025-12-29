# Auth Service Test Guide

This guide explains how to test the Auth Service from the gateway-service.

## Quick Start

Test the Auth Service:
```bash
cd /developer/Cloud_resource_management_system_platform_microservices/gateway-service
python scripts/test_auth_service.py
```

## Auth Service Configuration

The Auth Service should be running with the following configuration:

- **Service Name**: Auth Service
- **Base URL**: `http://127.0.0.1:8000`
- **Health Check**: `/health`
- **Routes**:
  - `/auth/login` - User login
  - `/auth/logout` - User logout
  - `/auth/register` - User registration
  - `/auth/refresh` - Token refresh

## Test Script

### Basic Usage

```bash
# Test with default URL (http://127.0.0.1:8000)
python scripts/test_auth_service.py

# Test with custom URL
python scripts/test_auth_service.py --url http://localhost:8000
```

### What It Tests

1. **Health Check** (`/health`)
   - Verifies service is running
   - Checks response status and service information

2. **Auth Routes**
   - `/auth/login` - Login endpoint
   - `/auth/logout` - Logout endpoint
   - `/auth/register` - Registration endpoint
   - `/auth/refresh` - Token refresh endpoint

## Expected Output

### Success Case

```
======================================================================
Auth Service Test
======================================================================

Service URL: http://127.0.0.1:8000
Health Check: /health
Auth Routes: 4 routes

🔍 Testing Health Check...
----------------------------------------------------------------------
✅ /health: Status: healthy, Service: auth-service, Version: 1.0.0

🔍 Testing Auth Routes...
----------------------------------------------------------------------
✅ /auth/login: HTTP 422 - validation error (expected)
✅ /auth/logout: HTTP 422 - validation error (expected)
✅ /auth/register: HTTP 422 - validation error (expected)
✅ /auth/refresh: HTTP 422 - validation error (expected)

======================================================================
Test Summary
======================================================================
Total Tests: 5
✅ Passed: 5
❌ Failed: 0

✅ All tests passed! Auth Service is ready.
```

### Failure Case (Service Not Running)

```
======================================================================
Auth Service Test
======================================================================

Service URL: http://127.0.0.1:8000
Health Check: /health
Auth Routes: 4 routes

🔍 Testing Health Check...
----------------------------------------------------------------------
❌ /health: Connection failed: Service not running at http://127.0.0.1:8000

🔍 Testing Auth Routes...
----------------------------------------------------------------------
❌ /auth/login: Connection failed: Service not running at http://127.0.0.1:8000
❌ /auth/logout: Connection failed: Service not running at http://127.0.0.1:8000
❌ /auth/register: Connection failed: Service not running at http://127.0.0.1:8000
❌ /auth/refresh: Connection failed: Service not running at http://127.0.0.1:8000

======================================================================
Test Summary
======================================================================
Total Tests: 5
✅ Passed: 0
❌ Failed: 5

Failed Tests:
  - /health: Connection failed: Service not running at http://127.0.0.1:8000
  - /auth/login: Connection failed: Service not running at http://127.0.0.1:8000
  - /auth/logout: Connection failed: Service not running at http://127.0.0.1:8000
  - /auth/register: Connection failed: Service not running at http://127.0.0.1:8000
  - /auth/refresh: Connection failed: Service not running at http://127.0.0.1:8000

❌ Some tests failed. Please check the issues above.
```

## Starting Auth Service

### Method 1: Direct Run

```bash
cd /developer/Cloud_resource_management_system_platform_microservices/auth-service
python run.py
```

### Method 2: Using uvicorn

```bash
cd /developer/Cloud_resource_management_system_platform_microservices/auth-service
uvicorn src.auth.main:app --reload --host 0.0.0.0 --port 8000
```

### Method 3: Docker

```bash
cd /developer/Cloud_resource_management_system_platform_microservices/auth-service
docker-compose up -d
```

## Verification Steps

### 1. Check Service is Running

```bash
# Health check
curl http://127.0.0.1:8000/health

# Expected response:
# {"status":"healthy","service":"auth-service","version":"1.0.0"}
```

### 2. Check Routes are Available

```bash
# Check OpenAPI schema
curl http://127.0.0.1:8000/openapi.json | jq '.paths | keys'

# Should include:
# - /health
# - /auth/login
# - /auth/logout
# - /auth/register
# - /auth/refresh
```

### 3. Test Individual Routes

```bash
# Test login endpoint (should return 422 validation error without credentials)
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{}'

# Test register endpoint
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Troubleshooting

### Service Not Running

**Error**: `Connection failed: Service not running at http://127.0.0.1:8000`

**Solution**:
1. Start the Auth Service:
   ```bash
   cd /developer/Cloud_resource_management_system_platform_microservices/auth-service
   python run.py
   ```

2. Verify it's running:
   ```bash
   curl http://127.0.0.1:8000/health
   ```

### Port Already in Use

**Error**: `[Errno 98] Address already in use`

**Solution**:
```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
export PORT=8001
python run.py
```

### Endpoint Not Found (404)

**Error**: `Endpoint not found (404)`

**Solution**:
1. Check if route is registered in `src/auth/main.py`
2. Verify route path matches exactly (case-sensitive)
3. Restart the service after code changes

### Database Connection Issues

**Error**: Database connection errors in Auth Service logs

**Solution**:
1. Ensure MySQL is running
2. Check database configuration in `.env.dev`
3. Verify database exists:
   ```bash
   mysql -u root -p -e "SHOW DATABASES LIKE 'auth_service';"
   ```

## Integration with Gateway

Once Auth Service is tested and running:

1. **Register with Service Discovery** (if using Nacos/Consul):
   - Auth Service should register itself on startup
   - Gateway will discover it automatically

2. **Configure Gateway Routes**:
   - Routes are already configured in `config/routes.yaml`
   - Gateway will forward `/auth/*` requests to Auth Service

3. **Test Through Gateway**:
   ```bash
   # Test through gateway (if gateway is running on port 8001)
   curl http://127.0.0.1:8001/auth/login \
     -X POST \
     -H "Content-Type: application/json" \
     -d '{"username":"test","password":"test"}'
   ```

## Test Checklist

- [ ] Auth Service is running on `http://127.0.0.1:8000`
- [ ] Health check endpoint `/health` returns 200
- [ ] `/auth/login` endpoint exists (returns 200, 400, 401, or 422)
- [ ] `/auth/logout` endpoint exists
- [ ] `/auth/register` endpoint exists
- [ ] `/auth/refresh` endpoint exists
- [ ] All tests pass: `python scripts/test_auth_service.py`

## Related Documentation

- `TEST_EXTERNAL_CONFIGURATION.md` - Testing all external services
- `EXTERNAL_SERVICES_CHECKLIST.md` - External services checklist
- `scripts/verify_external_services.py` - Comprehensive service verification
- Auth Service README - Auth Service documentation

## Summary

**Quick Test Command:**
```bash
python scripts/test_auth_service.py
```

**Expected Result:**
- ✅ Health check passes
- ✅ All 4 auth routes are accessible
- ✅ Service is ready for gateway integration
