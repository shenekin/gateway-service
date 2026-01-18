# How to Test External Configuration

This guide explains how to test all external service configurations for the gateway-service using `.env.dev`.

## Quick Start

### 1. Test All External Services (Recommended)

```bash
cd /developer/Cloud_resource_management_system_platform_microservices/gateway-service
python scripts/verify_external_services.py
```

This comprehensive script checks:
- ✅ Redis connection
- ✅ MySQL connection
- ✅ Database schema initialization
- ✅ Service discovery (Nacos/Consul/etcd/Static)
- ✅ Jaeger (optional)
- ✅ Backend services
- ✅ Log directory writability

### 2. Test Individual Services

#### Test Vault Configuration

```bash
python scripts/test_vault.py
```

This tests:
- Vault connection and authentication
- Reading JWT secrets (HS256, RS256)
- Health check

#### Test Database Connection

```bash
python scripts/database/init_database.py
# Or use the test script if available
```

#### Test Redis Connection

```bash
redis-cli -h localhost -p 6379 ping
# Expected: PONG
```

---

## Detailed Testing Guide

### Prerequisites

1. **Ensure `.env.dev` is configured**:
   ```bash
   # Check if .env.dev exists
   ls -la .env.dev
   
   # View configuration
   cat .env.dev | grep -E "(REDIS|MYSQL|VAULT|NACOS|CONSUL|ETCD)"
   ```

2. **Load environment from `.env.dev`**:
   The scripts automatically load from `.env.dev` using `python-dotenv`.

---

## Test Scripts Available

### 1. `scripts/verify_external_services.py` - Comprehensive Test

**Purpose**: Verify all external services are configured and accessible

**Usage**:
```bash
python scripts/verify_external_services.py
```

**What it checks**:
- [REQUIRED SERVICES]
  - Redis connection
  - MySQL connection
  - Database schema (6 required tables)
  - Log directory writability

- [OPTIONAL SERVICES]
  - Service discovery (Nacos/Consul/etcd/Static)
  - Jaeger availability
  - Backend services health

**Expected Output**:
```
============================================================
External Services Verification
============================================================

[REQUIRED SERVICES]
✅ Redis: Connected to localhost:6379
✅ MySQL: Connected to localhost:3306
✅ Database Schema: All 6 required tables exist
✅ Log Directory: Directory writable: /path/to/logs

[OPTIONAL SERVICES]
✅ Service Discovery (Static): Using static configuration from services.yaml
✅ Jaeger: Tracing disabled, not required
✅ Backend Services: Found 2 instances, 2 healthy

============================================================
VERIFICATION SUMMARY
============================================================
✅ All required services are available
✅ Gateway service can be started
```

**Exit Codes**:
- `0`: All required services available
- `1`: Some required services missing

---

### 2. `scripts/test_vault.py` - Vault Configuration Test

**Purpose**: Test HashiCorp Vault connection and secret retrieval

**Usage**:
```bash
python scripts/test_vault.py
```

**What it checks**:
1. Vault configuration from `.env.dev`
2. Vault connection and authentication (AppRole/Token)
3. Vault health status
4. Reading JWT secrets (HS256, RS256)
5. Reading raw secrets

**Expected Output**:
```
✅ Loaded environment from: .env.dev
======================================================================
Vault Integration Test
======================================================================

📋 Vault Configuration:
----------------------------------------------------------------------
  VAULT_ADDR: http://127.0.0.1:8200
  VAULT_AUTH_METHOD: approle
  JWT_VAULT_HS256_PATH: secret/jwt/hs256
  JWT_VAULT_RS256_PATH: secret/jwt/rs256
  VAULT_ROLE_ID: ✅ Set
  VAULT_SECRET_ID: ✅ Set

======================================================================

🔌 Testing Vault Connection...
----------------------------------------------------------------------
1. Initializing Vault client...
   ✅ Vault client initialized
2. Checking Vault connection...
   ✅ Connected and authenticated
3. Checking Vault health...
   Status: healthy
   Version: 1.x.x

======================================================================

🔐 Testing Secret Retrieval...
----------------------------------------------------------------------
4. Reading JWT HS256 secret from: secret/jwt/hs256
   ✅ Secret retrieved (length: 13 chars)
   Value: dev-jwt-hs256
5. Reading JWT RS256 secret from: secret/jwt/rs256
   ✅ Secret retrieved (length: 13 chars)
   Value: dev-jwt-rs256
6. Reading raw secret from: secret/jwt/hs256
   ✅ Raw secret data retrieved
   Keys: ['secret']

======================================================================
✅ All Vault tests completed successfully!
======================================================================
```

**Troubleshooting**:
- If Vault is sealed: `vault operator unseal <key>`
- If permission denied: See `VAULT_PERMISSION_FIX.md`
- If connection failed: Check `VAULT_ADDR` in `.env.dev`

---

## Manual Testing Methods

### Test Redis Configuration

```bash
# Using redis-cli
redis-cli -h localhost -p 6379 ping
# Expected: PONG

# With password (if configured)
redis-cli -h localhost -p 6379 -a <password> ping

# Test from Python
python -c "
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
print('✅ Redis connected' if r.ping() else '❌ Redis failed')
"
```

### Test MySQL Configuration

```bash
# Using mysql client
mysql -h localhost -P 3306 -u gateway_user -p gateway_db -e "SELECT 1"

# Test connection
python -c "
import asyncmy
import asyncio

async def test():
    conn = await asyncmy.connect(
        host='localhost',
        port=3306,
        user='gateway_user',
        password='gateway_password',
        db='gateway_db'
    )
    print('✅ MySQL connected')
    conn.close()

asyncio.run(test())
"
```

### Test Service Discovery

#### Nacos
```bash
curl http://localhost:8848/nacos/actuator/health
# Expected: {"status":"UP"}
```

#### Consul
```bash
curl http://localhost:8500/v1/status/leader
# Expected: "127.0.0.1:8300"
```

#### etcd
```bash
etcdctl --endpoints=localhost:2379 endpoint health
# Expected: localhost:2379 is healthy
```

### Test Vault Configuration

```bash
# Check Vault health
curl http://127.0.0.1:8200/v1/sys/health

# Test authentication (if using token)
export VAULT_TOKEN="<your-token>"
vault kv get secret/jwt/hs256

# Test AppRole authentication
vault write auth/approle/login \
    role_id="<role-id>" \
    secret_id="<secret-id>"
```

---

## Testing with .env.dev

### 1. Verify .env.dev is Loaded

```bash
# Check if .env.dev exists
ls -la .env.dev

# View Vault configuration
cat .env.dev | grep VAULT

# View Redis configuration
cat .env.dev | grep REDIS

# View MySQL configuration
cat .env.dev | grep MYSQL
```

### 2. Test Configuration Loading

```bash
python -c "
from dotenv import load_dotenv
import os

load_dotenv('.env.dev')
print('VAULT_ADDR:', os.getenv('VAULT_ADDR'))
print('REDIS_HOST:', os.getenv('REDIS_HOST'))
print('MYSQL_HOST:', os.getenv('MYSQL_HOST'))
"
```

### 3. Run Tests with .env.dev

All test scripts automatically load `.env.dev`:

```bash
# Comprehensive test (loads .env.dev automatically)
python scripts/verify_external_services.py

# Vault test (loads .env.dev automatically)
python scripts/test_vault.py
```

---

## Test Checklist

Before starting the gateway service, verify:

- [ ] **Redis**: `python scripts/verify_external_services.py` shows ✅ Redis
- [ ] **MySQL**: `python scripts/verify_external_services.py` shows ✅ MySQL
- [ ] **Database Schema**: All 6 tables exist
- [ ] **Vault**: `python scripts/test_vault.py` completes successfully
- [ ] **Service Discovery**: Configured and accessible
- [ ] **Log Directory**: Writable
- [ ] **Backend Services**: Running and registered

---

## Troubleshooting

### Redis Connection Failed

```bash
# Check Redis is running
redis-cli ping

# Check configuration
cat .env.dev | grep REDIS

# Test connection manually
python -c "
import redis
r = redis.Redis(host='localhost', port=6379)
print(r.ping())
"
```

### MySQL Connection Failed

```bash
# Check MySQL is running
systemctl status mysql

# Check configuration
cat .env.dev | grep MYSQL

# Test connection
mysql -h localhost -u gateway_user -p gateway_db
```

### Vault Connection Failed

```bash
# Check Vault is running
curl http://127.0.0.1:8200/v1/sys/health

# Check if sealed
vault status

# Unseal if needed
vault operator unseal <key>

# Check configuration
cat .env.dev | grep VAULT
```

### Service Discovery Failed

```bash
# Check Nacos
curl http://localhost:8848/nacos/v1/console/health

# Check Consul
curl http://localhost:8500/v1/status/leader

# Check etcd
etcdctl --endpoints=localhost:2379 endpoint health

# For static mode, check file exists
ls -la config/services.yaml
```

---

## Advanced Testing

### Test All Services Programmatically

```python
#!/usr/bin/env python3
"""Test all external services"""
import asyncio
from scripts.verify_external_services import ServiceVerifier
from app.utils.vault_util import VaultUtil

async def test_all():
    # Test external services
    verifier = ServiceVerifier()
    result = await verifier.verify_all()
    
    # Test Vault
    try:
        vault = VaultUtil()
        print(f"✅ Vault: Connected")
        jwt_secret = vault.get_jwt_secret("HS256")
        print(f"✅ Vault: JWT secret retrieved")
    except Exception as e:
        print(f"❌ Vault: {e}")
    
    return result["can_start"]

if __name__ == "__main__":
    success = asyncio.run(test_all())
    exit(0 if success else 1)
```

### Continuous Testing

```bash
# Watch mode - run tests every 30 seconds
watch -n 30 'python scripts/verify_external_services.py'
```

---

## Summary

**Quick Test Command**:
```bash
# Test everything
python scripts/verify_external_services.py && python scripts/test_vault.py
```

**Files**:
- `scripts/verify_external_services.py` - Comprehensive external services test
- `scripts/test_vault.py` - Vault-specific test
- `EXTERNAL_SERVICES_CHECKLIST.md` - Setup guide
- `VAULT_TEST_GUIDE.md` - Vault setup guide
- `VAULT_PERMISSION_FIX.md` - Vault permission troubleshooting

**Configuration**:
- All tests load from `.env.dev` automatically
- Environment variables take precedence
- See `EXTERNAL_SERVICES_CHECKLIST.md` for detailed setup



