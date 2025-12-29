# How to Run All Configuration Tests

## Quick Commands

### Method 1: Run All Configuration Tests (Recommended)

```bash
cd /developer/Cloud_resource_management_system_platform_microservices/gateway-service

# Using pytest directly
pytest tests/test_settings.py \
       tests/test_env_loader.py \
       tests/test_env_auto_create.py \
       tests/test_settings_env_switching.py \
       tests/test_settings_cluster.py \
       tests/test_circular_import_fix.py \
       tests/test_run.py \
       -v
```

### Method 2: Run Using Python Script

```bash
python scripts/run_config_tests.py
```

### Method 3: Run Individual Test Categories

```bash
# Basic settings tests
pytest tests/test_settings.py -v

# Environment loader tests
pytest tests/test_env_loader.py tests/test_env_auto_create.py -v

# Environment switching tests
pytest tests/test_settings_env_switching.py -v

# Cluster configuration tests
pytest tests/test_settings_cluster.py -v

# Import and integration tests
pytest tests/test_circular_import_fix.py tests/test_run.py -v
```

## Test Files

1. **`tests/test_settings.py`** - Basic settings functionality
   - Default values
   - Settings caching
   - Trusted proxy list
   - Allowed origins list

2. **`tests/test_env_loader.py`** - Environment file loading
   - Environment file path resolution
   - Loading from .env.dev, .env.prod, .env
   - Fallback behavior
   - Available environments

3. **`tests/test_env_auto_create.py`** - Auto-creation of env files
   - Creating example env files
   - Single/cluster mode configuration

4. **`tests/test_settings_env_switching.py`** - Environment switching
   - Loading with env_name parameter
   - Loading with env_file_path parameter
   - Reloading settings
   - Cache clearing

5. **`tests/test_settings_cluster.py`** - Cluster configuration
   - Deployment mode (single/cluster)
   - Single instance configuration
   - Cluster configuration
   - Redis/MySQL cluster

6. **`tests/test_circular_import_fix.py`** - Import fixes
   - Circular import prevention
   - Multiple imports

7. **`tests/test_run.py`** - Run script configuration
   - Argument parsing
   - Environment initialization
   - Server configuration

## Expected Output

When tests pass:
```
============================= test session starts ==============================
platform linux -- Python 3.10.14, pytest-7.4.3
collected 67 items

tests/test_settings.py::test_settings_default_values PASSED
tests/test_settings.py::test_settings_cached PASSED
...
============================= 67 passed in X.XXs ==============================
```

## Troubleshooting

### Some Tests Fail

Some tests may fail due to:
- Environment variable conflicts
- Missing .env files
- Configuration issues

**Solution**: Run tests individually to identify specific issues:
```bash
pytest tests/test_settings.py -v
```

### Import Errors

```bash
# Ensure dependencies are installed
pip install -r requirements.txt

# Ensure you're in the project root
cd /developer/Cloud_resource_management_system_platform_microservices/gateway-service
```

## Summary

**Quick Command:**
```bash
pytest tests/test_settings*.py tests/test_env*.py tests/test_circular_import_fix.py tests/test_run.py -v
```

**Test Count:** ~67 tests total

**Documentation:**
- `CONFIGURATION_TEST_GUIDE.md` - Detailed guide
- `TEST_EXTERNAL_CONFIGURATION.md` - External services testing
