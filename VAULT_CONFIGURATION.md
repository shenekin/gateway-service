# Vault Configuration Guide

This guide explains how to configure HashiCorp Vault connection settings in the gateway-service.

## Configuration Fields

All Vault configuration is available in the `Settings` class and can be set via environment variables or `.env` files.

### Basic Vault Connection

| Setting | Environment Variable | Default | Description |
|---------|---------------------|---------|-------------|
| `vault_enabled` | `VAULT_ENABLED` | `false` | Enable/disable Vault integration |
| `vault_addr` | `VAULT_ADDR` | `http://127.0.0.1:8200` | Vault server address |
| `vault_auth_method` | `VAULT_AUTH_METHOD` | `approle` | Authentication method (`approle` or `token`) |
| `vault_timeout` | `VAULT_TIMEOUT` | `5` | Connection timeout in seconds |
| `vault_verify` | `VAULT_VERIFY` | `true` | SSL certificate verification for HTTPS |

### Authentication Credentials

#### AppRole Authentication (Recommended)

| Setting | Environment Variable | Required | Description |
|---------|---------------------|----------|-------------|
| `vault_role_id` | `VAULT_ROLE_ID` | Yes (for approle) | AppRole role ID |
| `vault_secret_id` | `VAULT_SECRET_ID` | Yes (for approle) | AppRole secret ID |

#### Token Authentication

| Setting | Environment Variable | Required | Description |
|---------|---------------------|----------|-------------|
| `vault_token` | `VAULT_TOKEN` | Yes (for token) | Vault authentication token |

### Secret Paths

| Setting | Environment Variable | Default | Description |
|---------|---------------------|---------|-------------|
| `jwt_vault_hs256_path` | `JWT_VAULT_HS256_PATH` | `secret/jwt/hs256` | Path to HS256 JWT secret in Vault |
| `jwt_vault_rs256_path` | `JWT_VAULT_RS256_PATH` | `secret/jwt/rs256` | Path to RS256 JWT secret in Vault |
| `api_key_vault_path` | `API_KEY_VAULT_PATH` | `secret/api-keys` | Base path for API keys in Vault |

## Configuration Examples

### Example 1: Development Environment (`.env.dev`)

```bash
# Enable Vault
VAULT_ENABLED=true

# Vault connection
VAULT_ADDR=http://127.0.0.1:8200
VAULT_AUTH_METHOD=approle
VAULT_TIMEOUT=5
VAULT_VERIFY=false

# AppRole credentials
VAULT_ROLE_ID="27a54762-7a86-0048-1328-8d52d9dd55c9"
VAULT_SECRET_ID="ef654932-4a21-a5a5-113f-19fa7a4649a3"

# Secret paths
JWT_VAULT_HS256_PATH=secret/jwt/hs256
JWT_VAULT_RS256_PATH=secret/jwt/rs256
API_KEY_VAULT_PATH=secret/api-keys
```

### Example 2: Production Environment (`.env.prod`)

```bash
# Enable Vault
VAULT_ENABLED=true

# Vault connection (HTTPS)
VAULT_ADDR=https://vault.example.com:8200
VAULT_AUTH_METHOD=approle
VAULT_TIMEOUT=10
VAULT_VERIFY=true

# AppRole credentials (use secure secret management)
VAULT_ROLE_ID="${VAULT_ROLE_ID}"
VAULT_SECRET_ID="${VAULT_SECRET_ID}"

# Secret paths
JWT_VAULT_HS256_PATH=secret/jwt/hs256
JWT_VAULT_RS256_PATH=secret/jwt/rs256
API_KEY_VAULT_PATH=secret/api-keys
```

### Example 3: Token Authentication

```bash
# Enable Vault
VAULT_ENABLED=true

# Vault connection
VAULT_ADDR=http://127.0.0.1:8200
VAULT_AUTH_METHOD=token

# Token authentication
VAULT_TOKEN="hvs.xxxxxxxxxxxxxxxxxxxx"

# Secret paths
JWT_VAULT_HS256_PATH=secret/jwt/hs256
JWT_VAULT_RS256_PATH=secret/jwt/rs256
API_KEY_VAULT_PATH=secret/api-keys
```

## Using Vault Configuration in Code

### Access Settings

```python
from app.settings import get_settings

settings = get_settings()

# Check if Vault is enabled
if settings.vault_enabled:
    print(f"Vault address: {settings.vault_addr}")
    print(f"Auth method: {settings.vault_auth_method}")
```

### Using VaultUtil

The `VaultUtil` class automatically uses settings from the `Settings` class:

```python
from app.utils.vault_util import VaultUtil

# VaultUtil will use settings.vault_addr, settings.vault_auth_method, etc.
vault = VaultUtil()

# Get JWT secret (uses settings.jwt_vault_hs256_path)
jwt_secret = vault.get_jwt_secret("HS256")

# Get API key (uses settings.api_key_vault_path)
api_key = vault.get_api_key("gateway")
```

## Environment Variable Priority

The `VaultUtil` class uses the following priority:

1. **Settings class** (from `.env` files) - **Preferred**
2. **Environment variables** - Fallback for backward compatibility

This allows you to:
- Use `.env.dev` or `.env.prod` files for configuration
- Override with environment variables when needed
- Maintain backward compatibility with existing code

## Testing Vault Configuration

### Test Script

```bash
# Test Vault connection using .env.dev
python scripts/test_vault.py
```

### Verify Settings

```python
from app.settings import get_settings

settings = get_settings()
print(f"Vault enabled: {settings.vault_enabled}")
print(f"Vault address: {settings.vault_addr}")
print(f"Auth method: {settings.vault_auth_method}")
```

## Migration from Environment Variables

If you're currently using environment variables directly, the code will continue to work. However, it's recommended to:

1. **Add Vault settings to `.env.dev`**:
   ```bash
   VAULT_ENABLED=true
   VAULT_ADDR=http://127.0.0.1:8200
   VAULT_AUTH_METHOD=approle
   VAULT_ROLE_ID="your-role-id"
   VAULT_SECRET_ID="your-secret-id"
   ```

2. **Use Settings class** instead of `os.getenv()`:
   ```python
   # Old way (still works)
   vault_addr = os.getenv("VAULT_ADDR")
   
   # New way (recommended)
   from app.settings import get_settings
   settings = get_settings()
   vault_addr = settings.vault_addr
   ```

## Security Best Practices

1. **Never commit secrets** to version control
2. **Use AppRole authentication** instead of tokens in production
3. **Enable SSL verification** (`VAULT_VERIFY=true`) for HTTPS connections
4. **Use secure secret management** for `VAULT_ROLE_ID` and `VAULT_SECRET_ID` in production
5. **Set appropriate timeouts** based on network conditions
6. **Rotate credentials regularly**

## Troubleshooting

### Vault Not Connecting

1. Check `VAULT_ADDR` is correct
2. Verify Vault is running: `curl http://127.0.0.1:8200/v1/sys/health`
3. Check network connectivity
4. Verify SSL certificate if using HTTPS

### Authentication Failures

1. Verify `VAULT_ROLE_ID` and `VAULT_SECRET_ID` are correct (for AppRole)
2. Check `VAULT_TOKEN` is valid (for token auth)
3. Verify AppRole is enabled in Vault: `vault auth list`
4. Check AppRole permissions: `vault read auth/approle/role/gateway-service`

### Secret Path Errors

1. Verify secret paths exist in Vault: `vault kv get secret/jwt/hs256`
2. Check AppRole has permissions to read the path
3. Verify KV v2 secrets engine is enabled: `vault secrets list`

## Related Documentation

- `VAULT_TEST_GUIDE.md` - Testing Vault integration
- `VAULT_PERMISSION_FIX.md` - Fixing permission errors
- `TEST_EXTERNAL_CONFIGURATION.md` - Testing external services
- `app/utils/vault_util.py` - Vault utility implementation

## Summary

**Quick Configuration:**
```bash
# .env.dev
VAULT_ENABLED=true
VAULT_ADDR=http://127.0.0.1:8200
VAULT_AUTH_METHOD=approle
VAULT_ROLE_ID="your-role-id"
VAULT_SECRET_ID="your-secret-id"
JWT_VAULT_HS256_PATH=secret/jwt/hs256
JWT_VAULT_RS256_PATH=secret/jwt/rs256
API_KEY_VAULT_PATH=secret/api-keys
```

**Test Configuration:**
```bash
python scripts/test_vault.py
```
