#!/bin/bash
# Install all dependencies including PyJWT

set -e

echo "Installing gateway-service dependencies..."
echo "=========================================="
echo ""

# Get the Python executable
PYTHON="${PYTHON:-python}"

echo "Using Python: $($PYTHON --version)"
echo "Python path: $($PYTHON -c 'import sys; print(sys.executable)')"
echo ""

# Install from requirements.txt
echo "Installing from requirements.txt..."
$PYTHON -m pip install -r requirements.txt

echo ""
echo "Verifying PyJWT installation..."
$PYTHON -c "import jwt; print(f'✅ PyJWT {jwt.__version__} installed')"

echo ""
echo "✅ All dependencies installed!"
echo ""
echo "You can now start the project with:"
echo "  python run.py"
