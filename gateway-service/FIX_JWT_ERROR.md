# Fix JWT Import Error

## Problem
```
ModuleNotFoundError: No module named 'jwt'
```

## Solution

### Option 1: Install PyJWT Locally

```bash
cd /developer/Cloud_resource_management_system_platform_microservices/gateway-service
pip install PyJWT==2.8.0
```

Or install all dependencies:
```bash
pip install -r requirements.txt
```

### Option 2: If Using Docker

Rebuild the Docker image to include PyJWT:

```bash
cd /developer/Cloud_resource_management_system_platform_microservices/gateway-service
docker build -t gateway-service .
```

Or if using docker-compose:
```bash
docker-compose build
docker-compose up -d
```

### Option 3: If Using Virtual Environment

1. Activate virtual environment:
```bash
source venv/bin/activate
# or
source .venv/bin/activate
```

2. Install PyJWT:
```bash
pip install PyJWT==2.8.0
```

### Verification

Test if JWT works:
```bash
python -c "import jwt; print(f'✅ PyJWT {jwt.__version__} installed')"
```

## Current Status

- ✅ `PyJWT==2.8.0` is in `requirements.txt`
- ✅ PyJWT is installed in local Python environment
- ✅ All JWT functions are available

## If Error Persists

Please provide:
1. How you are running the application (Docker/local/virtualenv)
2. The exact error message and stack trace
3. The command you used to run it
4. Output of: `python --version` and `pip list | grep -i jwt`
