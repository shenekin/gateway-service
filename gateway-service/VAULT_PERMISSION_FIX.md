# Vault Permission Fix Guide

## Problem

Getting `permission denied` error when reading secrets from Vault, even though:
- Vault is unsealed
- Authentication works (AppRole login successful)
- Secrets exist in Vault

## Root Cause

The AppRole used by the gateway-service doesn't have a policy that grants permission to read from the `secret/data/jwt/*` paths.

## Solution

### Option 1: Use Setup Script (Recommended)

```bash
# Set your Vault root token
export VAULT_TOKEN="<your-root-token>"

# Run the setup script
cd /developer/Cloud_resource_management_system_platform_microservices/gateway-service
./scripts/setup_vault_policy.sh
```

This script will:
1. Create a policy `gateway-service-policy` with read permissions for JWT secrets
2. Create or update the AppRole to use this policy
3. Display the Role ID and Secret ID

### Option 2: Manual Setup

#### Step 1: Create Policy

```bash
export VAULT_ADDR="http://127.0.0.1:8200"
export VAULT_TOKEN="<your-root-token>"

# Create policy file
cat > gateway-service-policy.hcl <<EOF
path "secret/data/jwt/*" {
  capabilities = ["read"]
}

path "secret/data/api-keys/*" {
  capabilities = ["read"]
}

path "secret/metadata/jwt/*" {
  capabilities = ["list", "read"]
}

path "secret/metadata/api-keys/*" {
  capabilities = ["list", "read"]
}
EOF

# Write policy to Vault
vault policy write gateway-service-policy gateway-service-policy.hcl
```

#### Step 2: Update AppRole

```bash
# Get your Role ID from .env.dev
ROLE_ID="27a54762-7a86-0048-1328-8d52d9dd55c9"

# Find the role name (you may need to list roles first)
vault list auth/approle/role

# Update the role with the policy
vault write auth/approle/role/gateway-service \
    token_policies="gateway-service-policy" \
    secret_id_ttl=0 \
    token_ttl=0
```

#### Step 3: Generate New Secret ID

```bash
# Generate a new secret ID for the role
vault write -f auth/approle/role/gateway-service/secret-id
```

#### Step 4: Update .env.dev

Update the `VAULT_SECRET_ID` in `.env.dev` with the new secret ID.

### Option 3: Quick Fix (Development Only)

For development/testing, you can grant broader permissions:

```bash
# Create a policy with broader permissions (NOT for production!)
cat > dev-policy.hcl <<EOF
path "secret/data/*" {
  capabilities = ["read", "list"]
}

path "secret/metadata/*" {
  capabilities = ["read", "list"]
}
EOF

vault policy write dev-policy dev-policy.hcl
vault write auth/approle/role/gateway-service token_policies="dev-policy"
```

## Verify Fix

After setting up the policy, run the test:

```bash
python scripts/test_vault.py
```

You should see:
```
✅ Secret retrieved (length: X chars)
```

## Path Fix

The code has also been fixed to handle KV v2 paths correctly:
- Paths like `secret/jwt/hs256` are automatically converted to `jwt/hs256`
- This matches the KV v2 API which expects paths relative to the mount point

## Troubleshooting

### Still Getting Permission Denied?

1. **Check the policy**:
   ```bash
   vault policy read gateway-service-policy
   ```

2. **Check the AppRole**:
   ```bash
   vault read auth/approle/role/gateway-service
   ```

3. **Test with token**:
   ```bash
   # Login with AppRole to get a token
   vault write auth/approle/login \
       role_id="<role-id>" \
       secret_id="<secret-id>"
   
   # Use the token to test
   export VAULT_TOKEN="<token-from-above>"
   vault kv get secret/jwt/hs256
   ```

4. **Check mount point**:
   ```bash
   vault secrets list
   # Make sure 'secret/' is listed and is KV v2
   ```

## Files Updated

- `app/utils/vault_util.py`: Fixed path handling for KV v2
- `scripts/setup_vault_policy.sh`: New script to set up policies
- `VAULT_PERMISSION_FIX.md`: This guide
