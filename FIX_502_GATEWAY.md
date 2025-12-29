# Fix 502 Bad Gateway - Step by Step

## Problem
Gateway returns `502 Bad Gateway` because it cannot find auth-service instances.

## Root Cause
The gateway was started **before** updating `config/services.yaml`. Service discovery loads configuration at startup and keeps it in memory.

## Solution: Restart Gateway

### Step 1: Stop Current Gateway

```bash
# Find gateway process
ps aux | grep -E "gateway|uvicorn.*8001" | grep -v grep

# Stop gateway (choose one method):
# Method 1: Kill by process name
pkill -f "uvicorn.*8001"
pkill -f "gateway"

# Method 2: Kill by PID (if you see the process)
kill <PID>
```

### Step 2: Verify Config is Correct

```bash
cd /developer/Cloud_resource_management_system_platform_microservices/gateway-service

# Check auth-service config
cat config/services.yaml | grep -A 3 "auth-service:"
```

**Should show:**
```yaml
auth-service:
  instances:
    - url: http://127.0.0.1:8000  # ✅ Correct
```

**If it shows Docker names, fix it:**
```bash
# Fix config
sed -i 's|http://auth-service-1:8000|http://127.0.0.1:8000|g' config/services.yaml
sed -i 's|http://auth-service-2:8000|http://127.0.0.1:8000|g' config/services.yaml
```

### Step 3: Verify Auth Service is Running

```bash
# Test auth-service directly
curl http://127.0.0.1:8000/health
```

**Expected:**
```json
{"status":"healthy","service":"auth-service","version":"1.0.0"}
```

If it fails, start auth-service:
```bash
cd /developer/Cloud_resource_management_system_platform_microservices/auth-service
python run.py
```

### Step 4: Start Gateway

```bash
cd /developer/Cloud_resource_management_system_platform_microservices/gateway-service
python run.py
```

Or if using uvicorn directly:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Step 5: Verify Gateway Can Find Services

```bash
# Test service discovery
python -c "
from app.core.discovery import StaticServiceDiscovery
import asyncio

async def test():
    discovery = StaticServiceDiscovery()
    instances = await discovery.get_instances('auth-service')
    print(f'Found {len(instances)} instances:')
    for inst in instances:
        print(f'  - {inst.url}')

asyncio.run(test())
"
```

**Expected:**
```
Found 1 instances:
  - http://127.0.0.1:8000
```

### Step 6: Test Login Endpoint

```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alex.w", "password": "Ax9!kP3#Lm2Q"}'
```

**Should NOT return 502!**

## Quick Restart Script

Create `restart_gateway.sh`:

```bash
#!/bin/bash
echo "Stopping gateway..."
pkill -f "uvicorn.*8001" || pkill -f "gateway" || true
sleep 2

echo "Starting gateway..."
cd /developer/Cloud_resource_management_system_platform_microservices/gateway-service
python run.py &
sleep 3

echo "Testing gateway..."
curl -s http://localhost:8001/health | jq .
```

## Troubleshooting

### Still Getting 502?

1. **Check gateway logs:**
   ```bash
   tail -50 logs/error.log
   ```

2. **Verify service discovery:**
   ```bash
   python -c "
   from app.core.discovery import StaticServiceDiscovery
   import asyncio
   async def test():
       d = StaticServiceDiscovery()
       print(await d.get_instances('auth-service'))
   asyncio.run(test())
   "
   ```

3. **Check if auth-service is accessible:**
   ```bash
   curl http://127.0.0.1:8000/health
   ```

4. **Verify config file:**
   ```bash
   cat config/services.yaml | grep -A 5 "auth-service"
   ```

## Summary

**The fix is simple: RESTART THE GATEWAY!**

The configuration file is correct, but the running gateway process has the old configuration in memory. Restarting will load the new configuration.

```bash
# 1. Stop gateway
pkill -f "uvicorn.*8001"

# 2. Start gateway
cd /developer/Cloud_resource_management_system_platform_microservices/gateway-service
python run.py
```
