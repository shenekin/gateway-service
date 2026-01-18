# Nacos Service Registration Guide

This guide explains how to register microservices with Nacos service discovery.

## Prerequisites

1. **Nacos Server Running**
   ```bash
   # Check if Nacos is running
   curl http://localhost:8848/nacos/actuator/health
   
   # Or start Nacos with Docker
   docker run -d --name nacos -p 8848:8848 nacos/nacos-server:latest
   ```

2. **Gateway Configuration**
   ```bash
   # In .env.dev
   SERVICE_DISCOVERY_TYPE=nacos
   NACOS_SERVER_ADDRESSES=localhost:8848
   NACOS_NAMESPACE=public
   NACOS_GROUP=DEFAULT_GROUP
   ```

## Quick Start

### Register Single Service

```bash
# Register auth-service
python scripts/register_service_nacos.py \
  --service auth-service \
  --ip 127.0.0.1 \
  --port 8000
  ephemeral=False

# Register with metadata
python scripts/register_service_nacos.py \
  --service auth-service \
  --ip 127.0.0.1 \
  --port 8000 \
  --metadata '{"version":"1.0.0","health_check":"/health"}'
```

### Register Multiple Services

1. **Create configuration file** (`services_config.json`):

```json
{
  "nacos_server": "localhost:8848",
  "namespace": "public",
  "group": "DEFAULT_GROUP",
  "services": [
    {
      "name": "auth-service",
      "ip": "127.0.0.1",
      "port": 8000,
      "weight": 1.0,
      "metadata": {
        "version": "1.0.0",
        "health_check": "/health"
      }
    },
    {
      "name": "project-service",
      "ip": "127.0.0.1",
      "port": 8002,
      "weight": 1.0
    }
  ]
}
```

2. **Register all services**:

```bash
python scripts/register_service_nacos.py --config services_config.json
```

## Register Auth Service

### Method 1: Using Script

```bash
cd /developer/Cloud_resource_management_system_platform_microservices/gateway-service

python scripts/register_service_nacos.py \
  --service auth-service \
  --ip 127.0.0.1 \
  --port 8000 \
  --metadata '{"version":"1.0.0","health_check":"/health","description":"Authentication Service"}'
```

### Method 2: Using Python Code

Create a registration script in your auth-service:

```python
# auth-service/register_nacos.py
import sys
from pathlib import Path

# Add gateway-service to path to use NacosClientUtil
gateway_path = Path(__file__).parent.parent.parent / "gateway-service"
sys.path.insert(0, str(gateway_path))

from app.utils.nacos_client import NacosClientUtil
import os

def register_auth_service():
    """Register auth-service with Nacos"""
    client = NacosClientUtil(
        server_addresses=os.getenv("NACOS_SERVER_ADDRESSES", "localhost:8848"),
        namespace=os.getenv("NACOS_NAMESPACE", "public")
    )
    
    result = client.register_service(
        service_name="auth-service",
        ip="127.0.0.1",
        port=8000,
        group_name=os.getenv("NACOS_GROUP", "DEFAULT_GROUP"),
        weight=1.0,
        metadata={
            "version": "1.0.0",
            "health_check": "/health",
            "description": "Authentication and Authorization Service"
        }
    )
    
    if result:
        print("✅ Auth-service registered with Nacos")
    else:
        print("❌ Failed to register auth-service")
    
    return result

if __name__ == "__main__":
    register_auth_service()
```

### Method 3: Auto-Registration on Startup

Add to `auth-service/src/auth/main.py`:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting auth-service...")
    
    # ... existing startup code ...
    
    # Register with Nacos if enabled
    if os.getenv("NACOS_ENABLED", "false").lower() == "true":
        try:
            from app.utils.nacos_client import NacosClientUtil
            
            nacos_client = NacosClientUtil(
                server_addresses=os.getenv("NACOS_SERVER_ADDRESSES", "localhost:8848"),
                namespace=os.getenv("NACOS_NAMESPACE", "public")
            )
            
            result = nacos_client.register_service(
                service_name="auth-service",
                ip=os.getenv("SERVICE_IP", "127.0.0.1"),
                port=int(os.getenv("PORT", "8000")),
                group_name=os.getenv("NACOS_GROUP", "DEFAULT_GROUP"),
                metadata={
                    "version": settings.app_version,
                    "health_check": "/health"
                }
            )
            
            if result:
                logger.info("✅ Registered with Nacos")
            else:
                logger.warning("⚠️  Failed to register with Nacos")
        except Exception as e:
            logger.warning(f"⚠️  Nacos registration failed: {str(e)}")
    
    yield
    
    # Shutdown
    # Deregister from Nacos if needed
    logger.info("Shutting down auth-service...")
```

## Register Multiple Microservices

### Example Configuration

Create `services_config.json`:

```json
{
  "nacos_server": "localhost:8848",
  "namespace": "public",
  "group": "DEFAULT_GROUP",
  "services": [
    {
      "name": "auth-service",
      "ip": "127.0.0.1",
      "port": 8000,
      "weight": 1.0,
      "metadata": {
        "version": "1.0.0",
        "health_check": "/health"
      }
    },
    {
      "name": "project-service",
      "ip": "127.0.0.1",
      "port": 8002,
      "weight": 1.0,
      "metadata": {
        "version": "1.0.0",
        "health_check": "/health"
      }
    },
    {
      "name": "ecs-service",
      "ip": "127.0.0.1",
      "port": 8003,
      "weight": 1.0,
      "metadata": {
        "version": "1.0.0",
        "health_check": "/health"
      }
    },
    {
      "name": "dashboard-service",
      "ip": "127.0.0.1",
      "port": 8004,
      "weight": 1.0,
      "metadata": {
        "version": "1.0.0",
        "health_check": "/health"
      }
    }
  ]
}
```

### Register All Services

```bash
python scripts/register_service_nacos.py --config services_config.json
```

## Verify Registration

### Check in Nacos Console

1. Open Nacos Console: http://localhost:8848/nacos
2. Login (default: nacos/nacos)
3. Go to "Service Management" > "Service List"
4. You should see registered services

### Check via API

```bash
# List all services
curl "http://localhost:8848/nacos/v1/ns/service/list?pageNo=1&pageSize=10"

# Get service instances
curl "http://localhost:8848/nacos/v1/ns/instance/list?serviceName=auth-service&namespaceId=public"
```

### Check via Gateway

```bash
# Test if gateway can discover services
python -c "
from app.core.discovery import create_service_discovery
import asyncio

async def test():
    discovery = create_service_discovery()
    instances = await discovery.get_instances('auth-service')
    print(f'Found {len(instances)} instances:')
    for inst in instances:
        print(f'  - {inst.url}')

asyncio.run(test())
"
```

## Service Configuration

### Environment Variables

For each microservice, set:

```bash
# Nacos Configuration
NACOS_ENABLED=true
NACOS_SERVER_ADDRESSES=localhost:8848
NACOS_NAMESPACE=public
NACOS_GROUP=DEFAULT_GROUP

# Service Information
SERVICE_NAME=auth-service
SERVICE_IP=127.0.0.1
PORT=8000
```

### Gateway Configuration

In `gateway-service/.env.dev`:

```bash
SERVICE_DISCOVERY_TYPE=nacos
NACOS_SERVER_ADDRESSES=localhost:8848
NACOS_NAMESPACE=public
NACOS_GROUP=DEFAULT_GROUP
```

## Deregister Services

### Manual Deregistration

```bash
# Using Nacos API
curl -X DELETE "http://localhost:8848/nacos/v1/ns/instance?serviceName=auth-service&ip=127.0.0.1&port=8000&namespaceId=public"
```

### Automatic Deregistration

Services registered with `ephemeral=true` (default) will automatically deregister when they stop sending heartbeats.

## Troubleshooting

### Service Not Found

1. **Check Nacos is running:**
   ```bash
   curl http://localhost:8848/nacos/actuator/health
   ```

2. **Verify service is registered:**
   ```bash
   curl "http://localhost:8848/nacos/v1/ns/instance/list?serviceName=auth-service"
   ```

3. **Check gateway configuration:**
   ```bash
   # Verify SERVICE_DISCOVERY_TYPE is set to nacos
   grep SERVICE_DISCOVERY_TYPE .env.dev
   ```

### Connection Failed

1. **Check Nacos server address:**
   ```bash
   # Should match your Nacos server
   echo $NACOS_SERVER_ADDRESSES
   ```

2. **Test connection:**
   ```bash
   curl http://localhost:8848/nacos/v1/console/health
   ```

### Namespace Issues

If using custom namespace:

```bash
# Register with namespace
python scripts/register_service_nacos.py \
  --service auth-service \
  --ip 127.0.0.1 \
  --port 8000 \
  --namespace your-namespace

# Gateway must use same namespace
NACOS_NAMESPACE=your-namespace
```

## Best Practices

1. **Use Health Checks**: Always include health check endpoint in metadata
2. **Set Appropriate Weights**: Use weight for load balancing
3. **Use Ephemeral Instances**: Set `ephemeral=true` for auto-cleanup
4. **Monitor Heartbeats**: Ensure services send heartbeats regularly
5. **Use Namespaces**: Separate dev/staging/prod environments

## Summary

**Quick Commands:**

```bash
# Register single service
python scripts/register_service_nacos.py --service auth-service --ip 127.0.0.1 --port 8000

# Register multiple services
python scripts/register_service_nacos.py --config services_config.json

# Verify registration
curl "http://localhost:8848/nacos/v1/ns/instance/list?serviceName=auth-service"
```

**Configuration Files:**
- `scripts/services_config.json.example` - Example configuration
- `NACOS_SERVICE_REGISTRATION.md` - This guide
