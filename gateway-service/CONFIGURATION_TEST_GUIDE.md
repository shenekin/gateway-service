# Configuration Testing Guide

This guide explains how to run all configuration-related tests for the gateway-service.

## Quick Start

Run all configuration tests:
```bash
cd /developer/Cloud_resource_management_system_platform_microservices/gateway-service
python scripts/run_config_tests.py
```

## Test Categories

### 1. Settings Tests
Tests basic settings functionality:
- Default values
- Settings caching
- Trusted proxy list parsing
- Allowed origins list parsing

**Run individually:**
```bash
pytest tests/test_settings.py -v
```

### 2. Environment Loader Tests
Tests environment file loading:
- Environment file path resolution
- Loading from .env.dev, .env.prod, .env
- Fallback behavior
- Available environments detection

**Run individually:**
```bash
pytest tests/test_env_loader.py -v
pytest tests/test_env_auto_create.py -v
```

### 3. Environment Switching Tests
Tests switching between environments:
- Loading settings with env_name parameter
- Loading settings with env_file_path parameter
- Reloading settings
- Cache clearing
- Environment variable override

**Run individually:**
```bash
pytest tests/test_settings_env_switching.py -v
```

### 4. Cluster Configuration Tests
Tests cluster and single instance configuration:
- Deployment mode (single/cluster)
- Single instance configuration
- Cluster configuration
- Redis cluster configuration
- MySQL cluster configuration
- Cluster coordinator configuration
- Heartbeat and election timeout

**Run individually:**
```bash
pytest tests/test_settings_cluster.py -v
```

### 5. Import and Integration Tests
Tests settings import and integration:
- Circular import prevention
- Multiple imports
- Run script configuration

**Run individually:**
```bash
pytest tests/test_circular_import_fix.py -v
pytest tests/test_run.py -v
```

## Running All Tests

### Method 1: Using Test Runner Script (Recommended)

```bash
python scripts/run_config_tests.py
```

This script:
- Runs all configuration test files
- Groups tests by category
- Provides summary report
- Exits with appropriate code (0 for success, 1 for failure)

### Method 2: Using pytest Directly

```bash
# Run all configuration tests
pytest tests/test_settings.py \
       tests/test_env_loader.py \
       tests/test_env_auto_create.py \
       tests/test_settings_env_switching.py \
       tests/test_settings_cluster.py \
       tests/test_circular_import_fix.py \
       tests/test_run.py \
       -v

# Or use pattern matching
pytest tests/test_settings*.py tests/test_env*.py tests/test_circular_import_fix.py tests/test_run.py -v
```

### Method 3: Run Specific Category

```bash
# Only settings tests
pytest tests/test_settings.py -v

# Only environment tests
pytest tests/test_env_loader.py tests/test_env_auto_create.py -v

# Only cluster tests
pytest tests/test_settings_cluster.py -v
```

## Test Files Overview

| Test File | Description | Test Count |
|-----------|-------------|------------|
| `test_settings.py` | Basic settings functionality | 4 tests |
| `test_env_loader.py` | Environment file loading | 9 tests |
| `test_env_auto_create.py` | Auto-creation of env files | 6 tests |
| `test_settings_env_switching.py` | Environment switching | 10 tests |
| `test_settings_cluster.py` | Cluster configuration | 15+ tests |
| `test_circular_import_fix.py` | Import fixes | 10+ tests |
| `test_run.py` | Run script configuration | 8+ tests |

## Expected Output

When all tests pass:
```
======================================================================
Configuration Tests Runner
======================================================================

Running Settings Tests
======================================================================
✅ test_settings.py - PASSED

Running Environment Loader Tests
======================================================================
✅ test_env_loader.py - PASSED
✅ test_env_auto_create.py - PASSED

...

======================================================================
Test Summary
======================================================================

Total Tests: 7
✅ Passed: 7
❌ Failed: 0

✅ All configuration tests passed!
```

## Troubleshooting

### Import Errors

If you get import errors:
```bash
# Ensure you're in the project root
cd /developer/Cloud_resource_management_system_platform_microservices/gateway-service

# Install dependencies
pip install -r requirements.txt
```

### Test Failures

If tests fail:
1. Check if `.env.dev` exists and is properly configured
2. Verify all dependencies are installed
3. Check test output for specific error messages
4. Run individual test files to isolate issues

### Environment Variable Conflicts

Some tests modify environment variables. If tests fail:
```bash
# Clear environment variables
unset DEPLOYMENT_MODE CLUSTER_ENABLED PORT

# Run tests again
python scripts/run_config_tests.py
```

## Continuous Testing

### Watch Mode

```bash
# Install pytest-watch
pip install pytest-watch

# Watch for changes and rerun tests
ptw tests/test_settings*.py tests/test_env*.py
```

### Pre-commit Hook

Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
python scripts/run_config_tests.py
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
- name: Run Configuration Tests
  run: |
    cd gateway-service
    python scripts/run_config_tests.py
```

### GitLab CI Example

```yaml
test:configuration:
  script:
    - cd gateway-service
    - python scripts/run_config_tests.py
```

## Test Coverage

To check test coverage:
```bash
pytest tests/test_settings*.py tests/test_env*.py \
       --cov=app.settings \
       --cov=app.utils.env_loader \
       --cov-report=html
```

## Related Documentation

- `TEST_EXTERNAL_CONFIGURATION.md` - External services testing
- `EXTERNAL_SERVICES_CHECKLIST.md` - External services setup
- `VAULT_TEST_GUIDE.md` - Vault configuration testing
- `ENV_FILE_CONFIGURATION.md` - Environment file configuration

## Summary

**Quick Command:**
```bash
python scripts/run_config_tests.py
```

**Individual Test Files:**
- `tests/test_settings.py`
- `tests/test_env_loader.py`
- `tests/test_env_auto_create.py`
- `tests/test_settings_env_switching.py`
- `tests/test_settings_cluster.py`
- `tests/test_circular_import_fix.py`
- `tests/test_run.py`

All tests automatically use `.env.dev` configuration when available.
