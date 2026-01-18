#!/bin/bash
# Run all configuration-related tests

set -e

echo "======================================================================"
echo "Configuration Tests Runner"
echo "======================================================================"
echo ""

cd "$(dirname "$0")"

# Run all configuration tests
echo "Running all configuration tests..."
echo ""

pytest tests/test_settings.py \
       tests/test_env_loader.py \
       tests/test_env_auto_create.py \
       tests/test_settings_env_switching.py \
       tests/test_settings_cluster.py \
       tests/test_circular_import_fix.py \
       tests/test_run.py \
       -v

echo ""
echo "======================================================================"
echo "✅ All configuration tests completed!"
echo "======================================================================"
