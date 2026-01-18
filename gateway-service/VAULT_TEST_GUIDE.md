# Vault Integration Test Guide

## Overview

This guide explains how to test HashiCorp Vault integration with the gateway-service using `.env.dev` configuration.

## Prerequisites

1. **Install dependencies**:
   ```bash
   pip install hvac python-dotenv
   ```

2. **Vault Server**: Ensure HashiCorp Vault is running and accessible

## Configuration

The Vault configuration is loaded from `.env.dev`:

```env
# Vault paths
JWT_VAULT_HS256_PATH=secret/jwt/hs256
JWT_VAULT_RS256_PATH=secret/jwt/rs256

# Vault connection
VAULT_ADDR=http://127.0.0.1:8200
VAULT_AUTH_METHOD=approle
VAULT_ROLE_ID="your-role-id"
VAULT_SECRET_ID="your-secret-id"
```

## Running the Test

```bash
cd /developer/Cloud_resource_management_system_platform_microservices/gateway-service
python scripts/test_vault.py
```

## Test Steps

The test script performs the following checks:

1. **Configuration Check**: Verifies Vault configuration from `.env.dev`
2. **Connection Test**: Connects to Vault server
3. **Authentication**: Authenticates using AppRole method
4. **Health Check**: Checks Vault health status
5. **Secret Retrieval**: Tests reading JWT secrets from Vault

## Common Issues

### Vault is Sealed

**Error**: `Vault is sealed`

**Solution**:
```bash
# For development mode
vault operator unseal -address=http://127.0.0.1:8200 <unseal-key>

# Or start Vault in dev mode (auto-unsealed)
vault server -dev
```

### Vault Not Running

**Error**: `Connection refused` or `Failed to connect`

**Solution**:
1. Start Vault server:
   ```bash
   vault server -dev
   ```
2. Verify Vault is accessible:
   ```bash
   curl http://127.0.0.1:8200/v1/sys/health
   ```

### Authentication Failed

**Error**: `Failed to authenticate with Vault`

**Solution**:
1. Verify `VAULT_ROLE_ID` and `VAULT_SECRET_ID` in `.env.dev`
2. Check AppRole is enabled in Vault
3. Verify the role has proper permissions

## Setting Up Vault for Testing

### 1. Start Vault (Development Mode)

```bash
vault server -dev
```

This will:
- Start Vault on `http://127.0.0.1:8200`
- Auto-unseal Vault
- Display root token and unseal keys

### 2. Enable KV Secrets Engine

```bash
export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='<root-token-from-dev-mode>'

# Enable KV v2 secrets engine
vault secrets enable -version=2 -path=secret kv
```

### 3. Create Test Secrets

```bash
# Create JWT HS256 secret
vault kv put secret/jwt/hs256 secret="my-super-secret-jwt-key-hs256"

# Create JWT RS256 secret (if needed)
vault kv put secret/jwt/rs256 secret="my-super-secret-jwt-key-rs256"
```

### 4. Enable AppRole Auth Method

```bash
# Enable AppRole
vault auth enable approle

# Create AppRole
vault write auth/approle/role/gateway-service \
    token_policies="default" \
    secret_id_ttl=0 \
    token_ttl=0

# Get Role ID
vault read auth/approle/role/gateway-service/role-id

# Generate Secret ID
vault write -f auth/approle/role/gateway-service/secret-id
```

### 5. Update .env.dev

Update `.env.dev` with the Role ID and Secret ID:

```env
VAULT_ROLE_ID="<role-id-from-step-4>"
VAULT_SECRET_ID="<secret-id-from-step-4>"
```

## Vault Utility Usage

The `VaultUtil` class can be used in your code:

```python
from app.utils.vault_util import VaultUtil

# Initialize
vault = VaultUtil()

# Get JWT secret
jwt_secret = vault.get_jwt_secret("HS256")

# Get API key
api_key = vault.get_api_key("gateway")

# Read custom secret
secret_data = vault.read_secret("secret/my/path")
```

## Files Created

- `app/utils/vault_util.py`: Vault utility class
- `scripts/test_vault.py`: Test script
- `VAULT_TEST_GUIDE.md`: This guide

## Next Steps

1. Run the test script to verify Vault connection
2. Unseal Vault if needed
3. Create test secrets in Vault
4. Verify secret retrieval works correctly
