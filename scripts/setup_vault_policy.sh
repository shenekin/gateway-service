#!/bin/bash
# Setup Vault policy for gateway-service AppRole
# This script creates a policy that allows reading JWT secrets

set -e

VAULT_ADDR="${VAULT_ADDR:-http://127.0.0.1:8200}"
VAULT_TOKEN="${VAULT_TOKEN:-}"

if [ -z "$VAULT_TOKEN" ]; then
    echo "Error: VAULT_TOKEN environment variable is required"
    echo "Usage: VAULT_TOKEN=<your-token> ./setup_vault_policy.sh"
    exit 1
fi

export VAULT_ADDR

echo "Setting up Vault policy for gateway-service..."
echo "Vault Address: $VAULT_ADDR"
echo ""

# Create policy file
cat > /tmp/gateway-service-policy.hcl <<EOF
# Policy for gateway-service to read JWT secrets
path "secret/data/jwt/*" {
  capabilities = ["read"]
}

path "secret/data/api-keys/*" {
  capabilities = ["read"]
}

# Allow reading metadata
path "secret/metadata/jwt/*" {
  capabilities = ["list", "read"]
}

path "secret/metadata/api-keys/*" {
  capabilities = ["list", "read"]
}
EOF

echo "Policy file created: /tmp/gateway-service-policy.hcl"
echo ""

# Write policy to Vault
echo "Creating policy 'gateway-service-policy'..."
vault policy write gateway-service-policy /tmp/gateway-service-policy.hcl

echo ""
echo "✅ Policy created successfully!"
echo ""

# Get the AppRole name from .env.dev or use default
ROLE_NAME="${VAULT_ROLE_NAME:-gateway-service}"

echo "Updating AppRole '$ROLE_NAME' to use the policy..."
echo "Note: If the AppRole doesn't exist, you need to create it first:"
echo "  vault write auth/approle/role/$ROLE_NAME token_policies=\"gateway-service-policy\""
echo ""

# Try to update the role
if vault read auth/approle/role/$ROLE_NAME &>/dev/null; then
    vault write auth/approle/role/$ROLE_NAME token_policies="gateway-service-policy"
    echo "✅ AppRole updated successfully!"
else
    echo "⚠️  AppRole '$ROLE_NAME' not found. Creating it..."
    vault write auth/approle/role/$ROLE_NAME \
        token_policies="gateway-service-policy" \
        secret_id_ttl=0 \
        token_ttl=0
    
    echo "✅ AppRole created successfully!"
    echo ""
    echo "Get Role ID:"
    vault read auth/approle/role/$ROLE_NAME/role-id
    echo ""
    echo "Generate Secret ID:"
    vault write -f auth/approle/role/$ROLE_NAME/secret-id
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env.dev with the Role ID and Secret ID if needed"
echo "2. Run: python scripts/test_vault.py"
