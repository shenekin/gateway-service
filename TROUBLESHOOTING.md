# Troubleshooting Guide

## Cannot Start Project

If you're unable to start the project, follow these steps:

### 1. Check Port Availability

**Error:** `[Errno 98] error while attempting to bind on address ('0.0.0.0', 8001): address already in use`

**Solution:**
```bash
# Check if port 8001 is in use
lsof -i :8001
# or
netstat -tulpn | grep 8001

# Kill the process using port 8001
kill -9 <PID>

# Or use a different port
python run.py --port 8002
```

### 2. Check Python Dependencies

**Error:** `ModuleNotFoundError: No module named 'xxx'`

**Solution:**
```bash
# Install all dependencies
pip install -r requirements.txt

# Or use virtual environment
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Check Environment Configuration

**Error:** Missing configuration or environment variables

**Solution:**
```bash
# Create environment file
python run.py --create-env

# Or manually create .env file
cp .env.dev .env
# Edit .env with your configuration
```

### 4. Check External Services

**Error:** Connection errors to Redis, MySQL, etc.

**Solution:**
```bash
# Verify external services are running
python scripts/verify_external_services.py

# Start required services
# Redis
docker run -d --name redis -p 6379:6379 redis:latest

# MySQL
docker run -d --name mysql -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=rootpass \
  -e MYSQL_DATABASE=gateway_db \
  -e MYSQL_USER=gateway_user \
  -e MYSQL_PASSWORD=gateway_password \
  mysql:8.0
```

### 5. Check Database Initialization

**Error:** Database or table not found

**Solution:**
```bash
# Initialize database
python run.py --init-db

# Or manually
python scripts/database/init_database.py
```

### 6. Check Syntax Errors

**Error:** Syntax errors in code

**Solution:**
```bash
# Check Python syntax
python -m py_compile app/**/*.py

# Check imports
python -c "from app.main import app; print('OK')"
```

### 7. Check Logs

**Error:** Unknown errors

**Solution:**
```bash
# Run with verbose logging
python run.py --log-level debug

# Check log files
tail -f logs/application.log
tail -f logs/error.log
```

### 8. Common Issues

#### Issue: Request Body Reading Error

**Error:** `RuntimeError: Stream consumed` or body is empty

**Solution:** This has been fixed in the latest code. The request body is now stored in `request.state._body` and reused.

#### Issue: Rate Limiting Not Working Per-User

**Error:** All users share rate limit

**Solution:** This has been fixed. The code now extracts username/email from login request body for per-user rate limiting.

### 9. Quick Start Checklist

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create environment file
python run.py --create-env

# 3. Start external services (Redis, MySQL)
# See EXTERNAL_SERVICES_CHECKLIST.md

# 4. Initialize database
python run.py --init-db

# 5. Verify services
python scripts/verify_external_services.py

# 6. Start gateway
python run.py --env dev --reload
```

### 10. Get Help

If you're still having issues:

1. Check the error message carefully
2. Check logs in `logs/` directory
3. Verify all external services are running
4. Check environment variables in `.env` file
5. Try starting with `--log-level debug` for more information

## Common Error Messages

### `ImportError: cannot import name 'get_settings'`
- **Cause:** Circular import issue
- **Solution:** Already fixed. Use lazy imports in `app/settings.py`

### `ModuleNotFoundError: No module named 'jwt'`
- **Cause:** Missing PyJWT package
- **Solution:** `pip install PyJWT==2.8.0`

### `Connection refused` (Redis/MySQL)
- **Cause:** External service not running
- **Solution:** Start Redis/MySQL service

### `Address already in use`
- **Cause:** Port is already in use
- **Solution:** Use different port or kill existing process

