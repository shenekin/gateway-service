# Troubleshooting: 502 Bad Gateway

## Problem

Getting `502 Bad Gateway` error when accessing routes through gateway:

```
INFO: 127.0.0.1:54620 - "POST /auth/login HTTP/1.1" 502 Bad Gateway
```

## Root Cause

The gateway found the route but **cannot connect to the backend service**. This happens when:

1. **Service discovery cannot find service instances**
2. **Backend service is not running**
3. **Service URL in configuration is incorrect** (e.g., Docker service names in local dev)

## Solution

### Step 1: Check Backend Service is Running

```bash
# Check if auth-service is running
curl http://127.0.0.1:8000/health

# Expected response:
# {"status":"healthy","service":"auth-service","version":"1.0.0"}
```

If this fails, start the auth-service:
```bash
cd /developer/Cloud_resource_management_system_platform_microservices/auth-service
python run.py
```

### Step 2: Check Service Discovery Configuration

The gateway uses `config/services.yaml` to find backend services. For **local development**, it should use `127.0.0.1`:

```yaml
services:
  auth-service:
    instances:
      - url: http://127.0.0.1:8000  # ✅ Correct for local dev
        weight: 1
        healthy: true
```

**Common mistake**: Using Docker service names in local dev:
```yaml
# ❌ Wrong for local development
- url: http://auth-service-1:8000
- url: http://auth-service-2:8000
```

### Step 3: Verify Service Discovery

Check if gateway can find the service:

```bash
cd /developer/Cloud_resource_management_system_platform_microservices/gateway-service
python -c "
from app.core.discovery import create_service_discovery
import asyncio

async def check():
    discovery = create_service_discovery()
    instances = await discovery.get_instances('auth-service')
    print(f'Found {len(instances)} auth-service instances:')
    for inst in instances:
        print(f'  - {inst.url} (healthy: {inst.healthy})')

asyncio.run(check())
"
```

**Expected output:**
```
Found 1 auth-service instances:
  - http://127.0.0.1:8000 (healthy: True)
```

If it shows `Found 0 instances`, the service is not configured correctly.

### Step 4: Restart Gateway

After fixing `config/services.yaml`, restart the gateway:

```bash
# Stop gateway
pkill -f "gateway"

# Restart gateway
cd /developer/Cloud_resource_management_system_platform_microservices/gateway-service
python run.py
```

## Quick Fix for Local Development

### Option 1: Update services.yaml

Edit `config/services.yaml`:

```yaml
services:
  auth-service:
    instances:
      - url: http://127.0.0.1:8000
        weight: 1
        healthy: true
```

### Option 2: Use Environment Variable (if supported)

Some configurations allow overriding service URLs via environment variables.

## Verification

### 1. Test Direct Connection

```bash
# Test auth-service directly
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alex.w", "password": "Ax9!kP3#Lm2Q"}'
```

### 2. Test Through Gateway

```bash
# Test through gateway
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alex.w", "password": "Ax9!kP3#Lm2Q"}'
```

### 3. Check Gateway Logs

```bash
# View error logs
tail -50 logs/error.log

# Look for connection errors
grep -i "connection\|502\|bad gateway" logs/error.log
```

## Common Issues

### Issue 1: Service Not Running

**Error**: `502 Bad Gateway` or `Service auth-service not available`

**Solution**:
```bash
# Start auth-service
cd /developer/Cloud_resource_management_system_platform_microservices/auth-service
python run.py
```

### Issue 2: Wrong Service URL

**Error**: Connection timeout or DNS resolution failure

**Solution**: Update `config/services.yaml` to use `http://127.0.0.1:8000` for local dev

### Issue 3: Service Discovery Type Mismatch

**Error**: Service instances not found

**Check**: Verify `SERVICE_DISCOVERY_TYPE` in `.env.dev`:
```bash
# For static service discovery (local dev)
SERVICE_DISCOVERY_TYPE=static

# For Nacos (if using service registry)
SERVICE_DISCOVERY_TYPE=nacos
```

### Issue 4: Port Mismatch

**Error**: Connection refused

**Check**: Verify auth-service is running on port 8000:
```bash
# Check if port 8000 is in use
lsof -i :8000

# Or test directly
curl http://127.0.0.1:8000/health
```

## Debugging Steps

1. **Check backend service health**:
   ```bash
   curl http://127.0.0.1:8000/health
   ```

2. **Check service discovery**:
   ```bash
   python -c "
   from app.core.discovery import create_service_discovery
   import asyncio
   async def check():
       discovery = create_service_discovery()
       instances = await discovery.get_instances('auth-service')
       print(f'Instances: {len(instances)}')
       for inst in instances:
           print(f'  {inst.url}')
   asyncio.run(check())
   "
   ```

3. **Check gateway logs**:
   ```bash
   tail -f logs/error.log
   ```

4. **Test direct connection**:
   ```bash
   curl -X POST http://127.0.0.1:8000/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username": "test", "password": "test"}'
   ```

## Summary

**Quick Checklist:**
- [ ] Auth-service is running on `http://127.0.0.1:8000`
- [ ] `config/services.yaml` has correct URL (`http://127.0.0.1:8000`)
- [ ] Gateway is restarted after config change
- [ ] Service discovery can find auth-service instances
- [ ] Direct connection to auth-service works

**Quick Fix:**
```bash
# 1. Update config/services.yaml
# Change: http://auth-service-1:8000
# To:     http://127.0.0.1:8000

# 2. Restart gateway
pkill -f gateway && python run.py
```
