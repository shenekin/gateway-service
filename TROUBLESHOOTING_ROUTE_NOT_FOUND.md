# Troubleshooting: Route Not Found

## Problem

Getting "Route not found" error when accessing auth endpoints:

```bash
# ❌ Wrong paths
curl -X POST http://localhost:8001/login
# {"detail":"Route not found: POST /login"}

curl -X POST http://localhost:8001/api/auth/login
# {"detail":"Route not found: POST /api/auth/login"}
```

## Solution

### ✅ Correct Path Format

The gateway routes are configured **without** `/api` prefix. Use:

```bash
# ✅ Correct path
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alex.w", "password": "Ax9!kP3#Lm2Q"}'
```

### Available Auth Routes

All auth routes are under `/auth/` prefix (no `/api`):

- ✅ `POST /auth/login` - User login
- ✅ `POST /auth/logout` - User logout  
- ✅ `POST /auth/register` - User registration
- ✅ `POST /auth/refresh` - Token refresh

### Route Configuration

Routes are defined in `config/routes.yaml`:

```yaml
routes:
  - path: /auth/login
    service: auth-service
    methods: [POST]
    auth_required: false
```

**Note**: There is **no `/api` prefix** in the route configuration.

## Common Mistakes

### ❌ Mistake 1: Missing `/auth` prefix

```bash
# ❌ Wrong
curl -X POST http://localhost:8001/login

# ✅ Correct
curl -X POST http://localhost:8001/auth/login
```

### ❌ Mistake 2: Adding `/api` prefix

```bash
# ❌ Wrong
curl -X POST http://localhost:8001/api/auth/login

# ✅ Correct
curl -X POST http://localhost:8001/auth/login
```

### ❌ Mistake 3: Wrong HTTP method

```bash
# ❌ Wrong (login requires POST, not GET)
curl http://localhost:8001/auth/login

# ✅ Correct
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alex.w", "password": "Ax9!kP3#Lm2Q"}'
```

## Verification Steps

### 1. Check Gateway is Running

```bash
curl http://localhost:8001/health
# Expected: {"status":"healthy","service":"gateway-service"}
```

### 2. Check Route Configuration

```bash
# View routes configuration
cat config/routes.yaml | grep -A 5 "auth/login"
```

Should show:
```yaml
  - path: /auth/login
    service: auth-service
    methods: [POST]
```

### 3. Test Correct Path

```bash
# Test login endpoint
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alex.w", "password": "Ax9!kP3#Lm2Q"}'
```

### 4. Check Auth Service is Running

```bash
# Direct check to auth service
curl http://127.0.0.1:8000/health
# Expected: {"status":"healthy","service":"auth-service","version":"1.0.0"}
```

### 5. Check Service Discovery

If using service discovery (Nacos/Consul), verify auth-service is registered:

```bash
# Check if auth-service instances are available
python scripts/verify_external_services.py
```

## Troubleshooting Internal Server Error

If you get "Internal Server Error" after fixing the path:

### 1. Check Gateway Logs

```bash
# View error logs
tail -50 logs/error.log

# View all logs
tail -50 logs/application.log
```

### 2. Check Auth Service Logs

```bash
# If auth service is running locally
cd /developer/Cloud_resource_management_system_platform_microservices/auth-service
tail -50 logs/*.log
```

### 3. Verify Auth Service is Accessible

```bash
# Test direct connection to auth service
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alex.w", "password": "Ax9!kP3#Lm2Q"}'
```

### 4. Check Service Discovery

The gateway needs to find auth-service instances:

```bash
# Run service verification
python scripts/verify_external_services.py
```

Look for:
```
✅ Backend Services: Found X instances, X healthy
```

If it shows "No backend service instances found", the auth-service is not registered with service discovery.

## Quick Test Script

Create a test script to verify all paths:

```bash
#!/bin/bash
# test_auth_routes.sh

BASE_URL="http://localhost:8001"

echo "Testing Auth Routes..."
echo ""

# Test health
echo "1. Health check:"
curl -s "$BASE_URL/health" | jq .
echo ""

# Test login
echo "2. Login endpoint:"
curl -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "alex.w", "password": "Ax9!kP3#Lm2Q"}' \
  -w "\nHTTP Status: %{http_code}\n"
echo ""

# Test register
echo "3. Register endpoint:"
curl -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test123"}' \
  -w "\nHTTP Status: %{http_code}\n"
echo ""
```

## Summary

**Correct Path Format:**
```
http://localhost:8001/auth/login  ✅
http://localhost:8001/auth/logout  ✅
http://localhost:8001/auth/register  ✅
http://localhost:8001/auth/refresh  ✅
```

**Wrong Path Formats:**
```
http://localhost:8001/login  ❌ (missing /auth prefix)
http://localhost:8001/api/auth/login  ❌ (no /api prefix)
```

**Quick Fix:**
```bash
# Use /auth/login instead of /login or /api/auth/login
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alex.w", "password": "Ax9!kP3#Lm2Q"}'
```
