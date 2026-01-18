#!/bin/bash
# Fix auth-service configuration for local development

set -e

CONFIG_FILE="config/services.yaml"
BACKUP_FILE="config/services.yaml.backup"

echo "🔧 Fixing auth-service configuration for local development..."
echo ""

# Backup original config
if [ ! -f "$BACKUP_FILE" ]; then
    cp "$CONFIG_FILE" "$BACKUP_FILE"
    echo "✅ Backed up original config to $BACKUP_FILE"
fi

# Update auth-service URL to localhost
sed -i 's|http://auth-service-1:8000|http://127.0.0.1:8000|g' "$CONFIG_FILE"
sed -i 's|http://auth-service-2:8000|http://127.0.0.1:8000|g' "$CONFIG_FILE"

echo "✅ Updated auth-service URLs to http://127.0.0.1:8000"
echo ""
echo "📋 Current configuration:"
grep -A 3 "auth-service:" "$CONFIG_FILE"
echo ""
echo "⚠️  IMPORTANT: Restart the gateway service for changes to take effect!"
echo ""
echo "To restart:"
echo "  1. Stop gateway: pkill -f gateway"
echo "  2. Start gateway: python run.py"
