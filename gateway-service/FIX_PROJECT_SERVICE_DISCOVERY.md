# Fix: Project Service Not Available

**Date:** 2024-12-30  
**Issue:** `{"detail":"Service project-service not available"}`  
**Status:** ✅ Fixed

## Problem

Gateway-service cannot discover project-service because:
1. Service discovery was trying to use NACOS (default) but project-service is not registered
2. Static service configuration had wrong URL for project-service

## Solution Applied

### 1. Fixed Static Service Configuration

**File:** `gateway-service/config/services.yaml`

**Before (Wrong):**
```yaml
project-service:
  instances:
    - url: http://project-service-1:8000  # Wrong URL
```

**After (Correct):**
```yaml
project-service:
  instances:
    - url: http://127.0.0.1:8002  # Correct URL (project-service runs on port 8002)
```

### 2. Set Service Discovery Type to Static

**File:** `gateway-service/.env`

Added:
```bash
SERVICE_DISCOVERY_TYPE=static
```

This tells gateway-service to use static configuration from `config/services.yaml` instead of trying to use NACOS.

## Current Configuration

**gateway-service/config/services.yaml:**
```yaml
services:
  project-service:
    instances:
      - url: http://127.0.0.1:8002
        weight: 1
        healthy: true
    health_check:
      path: /health
      interval: 30
      timeout: 5
      
  auth-service:
    instances:
      - url: http://127.0.0.1:8000
        weight: 1
        healthy: true
    health_check:
      path: /health
      interval: 30
      timeout: 5
```

**gateway-service/.env:**
```bash
SERVICE_DISCOVERY_TYPE=static
```

## Next Steps

### 1. Restart Gateway-Service

**IMPORTANT:** You must restart gateway-service for the changes to take effect:

```bash
cd gateway-service
# Stop current process and restart
python run.py
```

### 2. Test

After restarting, test the endpoint:

```bash
# Get token
TOKEN=$(curl -s -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alex.w","password":"Ax9!kP3#Lm2Q"}' | jq -r '.access_token')

# Test project creation
curl -X POST http://localhost:8001/api/v1/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"customer_id": 1, "name": "Test Project"}'
```

**Expected:** Should return 200/201 with project data, NOT "Service project-service not available"

## Service Discovery Options

Gateway-service supports three service discovery types:

### 1. Static (Current - Recommended for Development)

Uses `config/services.yaml` file. No external service discovery needed.

**Configuration:**
```bash
SERVICE_DISCOVERY_TYPE=static
```

**Pros:**
- Simple setup
- No external dependencies
- Good for development

**Cons:**
- Manual configuration
- No automatic service discovery

### 2. Nacos (Production)

Uses Nacos for service discovery. Services must register themselves with Nacos.

**Configuration:**
```bash
SERVICE_DISCOVERY_TYPE=nacos
NACOS_SERVER_ADDRESSES=localhost:8848
NACOS_NAMESPACE=public
NACOS_GROUP=DEFAULT_GROUP
```

**Pros:**
- Automatic service discovery
- Health checks
- Load balancing

**Cons:**
- Requires Nacos server running
- Services must register with Nacos

### 3. Consul

Uses Consul for service discovery.

**Configuration:**
```bash
SERVICE_DISCOVERY_TYPE=consul
CONSUL_HOST=localhost
CONSUL_PORT=8500
```

## Verification

Verify project-service is accessible:

```bash
# Check project-service health directly
curl http://localhost:8002/health

# Should return: {"status":"healthy","service":"project-service"}
```

## Troubleshooting

If you still get "Service project-service not available":

1. **Check project-service is running:**
   ```bash
   curl http://localhost:8002/health
   ```

2. **Check services.yaml has correct URL:**
   ```bash
   cat gateway-service/config/services.yaml | grep -A 5 "project-service"
   ```

3. **Verify SERVICE_DISCOVERY_TYPE is set:**
   ```bash
   grep SERVICE_DISCOVERY_TYPE gateway-service/.env
   ```

4. **Restart gateway-service** after making changes

5. **Check gateway-service logs** for discovery errors

## Summary

✅ **Fixed:** Updated `config/services.yaml` with correct project-service URL (http://127.0.0.1:8002)  
✅ **Fixed:** Set `SERVICE_DISCOVERY_TYPE=static` in `.env`  
✅ **Status:** Configuration updated, restart gateway-service to apply changes

