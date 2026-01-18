# Unified Entry Point and Port Update - 2024-12-19

## Overview

Added unified entry point (`run.py`) for gateway service and updated default port from 8000 to 8001.

## Changes Made

### 1. New Unified Entry Point

**File Created:**
- `run.py`: Unified entry point script for starting the gateway service

**Features:**
- Command-line argument parsing
- Environment selection (default, dev, prod)
- Host and port configuration
- Auto-reload support
- Worker process configuration
- Deployment mode selection
- Environment file auto-creation
- Database initialization on startup
- Comprehensive error handling

**Key Functions:**
- `parse_arguments()`: Parse command line arguments (lines 18-95)
- `initialize_environment()`: Initialize environment with auto-creation (lines 78-90)
- `initialize_database()`: Initialize database if requested (lines 92-105)
- `get_server_config()`: Get server configuration from args and settings (lines 107-125)
- `main()`: Main entry point (lines 127-165)

### 2. Port Updates

**Files Modified:**

1. **`app/settings.py`**
   - Line 19: Changed default port from 8000 to 8001
   - Line 114: Changed single instance port from 8000 to 8001

2. **`scripts/create_env_examples.py`**
   - Updated default PORT to 8001
   - Updated SINGLE_INSTANCE_PORT to 8001

3. **`Dockerfile`**
   - Updated EXPOSE port to 8001
   - Updated health check port to 8001
   - Changed CMD to use `run.py` instead of direct uvicorn

4. **`tests/test_settings.py`**
   - Updated port assertion from 8000 to 8001

5. **`app/main.py`**
   - Added deprecation warning for direct execution
   - Recommends using `run.py` instead

### 3. Test Coverage

**New Test File:**
- `tests/test_run.py`: Comprehensive tests for run.py entry point

**Test Coverage:**
- 20 test methods covering:
  - Argument parsing (8 tests)
  - Environment initialization (2 tests)
  - Database initialization (2 tests)
  - Server configuration (3 tests)
  - Main function execution (3 tests)
  - Error handling (2 tests)

## Usage Examples

### Basic Usage

```bash
# Start with default settings
python run.py

# Start with development environment
python run.py --env dev

# Start with production environment
python run.py --env prod
```

### Advanced Usage

```bash
# Development with auto-reload
python run.py --env dev --reload

# Production with multiple workers
python run.py --env prod --workers 4

# Custom host and port
python run.py --host 127.0.0.1 --port 9000

# With environment file auto-creation
python run.py --env dev --create-env

# With database initialization
python run.py --env dev --init-db

# Cluster mode
python run.py --env prod --deployment-mode cluster
```

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--env` | Environment name (default, dev, prod) | None (uses ENVIRONMENT var) |
| `--host` | Host to bind to | From settings (0.0.0.0) |
| `--port` | Port to bind to | From settings (8001) |
| `--reload` | Enable auto-reload | False |
| `--workers` | Number of worker processes | 1 |
| `--deployment-mode` | Deployment mode (single, cluster) | From settings |
| `--log-level` | Log level | From settings |
| `--create-env` | Create example .env file | False |
| `--init-db` | Initialize database | False |

## Port Configuration

### Default Port: 8001

The default port has been updated from 8000 to 8001. This can be configured via:

1. **Environment Variable:**
   ```bash
   export PORT=8001
   python run.py
   ```

2. **Command Line:**
   ```bash
   python run.py --port 8001
   ```

3. **Environment File:**
   ```bash
   # In .env file
   PORT=8001
   ```

### Port References Updated

- Gateway service default port: 8000 → 8001
- Single instance port: 8000 → 8001
- Docker EXPOSE: 8000 → 8001
- Health check: 8000 → 8001

**Note:** Backend service ports (in config/services.yaml) remain unchanged as they are separate services.

## Backward Compatibility

✅ **All existing functionality preserved:**
- Direct execution of `app.main` still works (with deprecation warning)
- All existing APIs unchanged
- All existing tests pass
- Environment variable configuration still works

## Code Quality

✅ **Follows Coding Standards:**
- All functions have docstrings
- Type hints throughout
- English comments only
- Proper error handling
- Comprehensive test coverage
- Clear code structure

## Testing

Run tests for the new entry point:

```bash
pytest tests/test_run.py -v
```

All 20 tests should pass, covering:
- Argument parsing
- Environment initialization
- Database initialization
- Server configuration
- Main function execution
- Error handling

## Migration Guide

### From Direct Execution

**Before:**
```bash
python -m app.main
# or
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**After:**
```bash
python run.py
# or
python run.py --host 0.0.0.0 --port 8001
```

### From Environment Variables

**Before:**
```bash
export PORT=8000
python -m app.main
```

**After:**
```bash
export PORT=8001
python run.py
# or
python run.py --port 8001
```

## Files Summary

### Created
- `run.py`: Unified entry point
- `tests/test_run.py`: Entry point tests
- `ENTRY_POINT_UPDATE_2024-12-19.md`: This document

### Modified
- `app/settings.py`: Port updates (lines 19, 114)
- `scripts/create_env_examples.py`: Port updates
- `Dockerfile`: Port and CMD updates
- `app/main.py`: Deprecation warning
- `tests/test_settings.py`: Port assertion update
- `README.md`: Documentation updates

## Next Steps

1. Use `python run.py` as the standard way to start the service
2. Update deployment scripts to use the new entry point
3. Update documentation references to port 8001
4. Consider removing direct execution support in future versions

