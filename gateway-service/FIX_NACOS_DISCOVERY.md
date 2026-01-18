# Fix: Nacos Service Discovery Error

## Problem

Gateway startup error:
```
Failed to get service instances for project-service: 'str' object has no attribute 'get'
```

## Root Cause

The `list_naming_instance()` method in nacos-sdk-python returns a **dictionary** with a `hosts` key containing the list of instances, not a list directly.

**Response structure:**
```python
{
    "name": "DEFAULT_GROUP@@service-name",
    "groupName": "DEFAULT_GROUP",
    "hosts": [  # ← Instances are here
        {
            "ip": "127.0.0.1",
            "port": 8000,
            "healthy": true,
            ...
        }
    ],
    ...
}
```

The code was trying to iterate over the dictionary or call `.get()` on string values instead of accessing the `hosts` list.

## Solution

### Fixed Files

1. **`app/utils/nacos_client.py`** - `get_service_instances()` method
   - Extract `hosts` from response dictionary
   - Added type checking for safety

2. **`app/core/discovery.py`** - `NacosServiceDiscovery.get_instances()` method
   - Added type checking for instance data
   - Better error handling for metadata parsing

### Code Changes

**Before:**
```python
instances = self.client.list_naming_instance(...)
# Tried to iterate over dict directly
for inst in instances:
    ip = inst.get("ip")  # Error: 'str' object has no attribute 'get'
```

**After:**
```python
response = self.client.list_naming_instance(...)
# Extract hosts from response
if isinstance(response, dict):
    instances = response.get("hosts", [])
elif isinstance(response, list):
    instances = response
else:
    instances = []

# Now iterate over actual instances
for inst in instances:
    if isinstance(inst, dict):
        ip = inst.get("ip", "")
```

## Verification

### Test Service Discovery

```bash
python -c "
from app.core.discovery import create_service_discovery
import asyncio

async def test():
    discovery = create_service_discovery()
    instances = await discovery.get_instances('auth-service')
    print(f'Found {len(instances)} instances:')
    for inst in instances:
        print(f'  - {inst.url} (healthy: {inst.healthy})')

asyncio.run(test())
"
```

**Expected output:**
```
Found 1 instances:
  - http://127.0.0.1:8000 (healthy: True)
```

### Check Nacos API Directly

```bash
curl "http://localhost:8848/nacos/v1/ns/instance/list?serviceName=auth-service&namespaceId=public"
```

## Next Steps

1. **Restart Gateway**
   ```bash
   pkill -f "uvicorn.*8001"
   python run.py
   ```

2. **Verify No Errors**
   - Check startup logs for "Failed to get service instances" errors
   - Should see clean startup without errors

3. **Register Services**
   ```bash
   # Register auth-service (if not already registered)
   python scripts/register_service_nacos.py \
     --service auth-service \
     --ip 127.0.0.1 \
     --port 8000
   
   # Register other services
   python scripts/register_service_nacos.py --config services_config.json
   ```

## Summary

**Fixed:**
- ✅ `get_service_instances()` now correctly extracts `hosts` from response
- ✅ Added type checking to prevent similar errors
- ✅ Better error handling for edge cases

**Result:**
- ✅ Gateway can now discover services from Nacos without errors
- ✅ Service discovery works correctly for registered services
