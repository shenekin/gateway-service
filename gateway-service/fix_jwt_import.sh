#!/bin/bash
# Fix JWT import error by ensuring PyJWT is installed

echo "Fixing JWT import error..."
echo "=========================="
echo ""

# Check if running in virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    echo "Virtual environment detected: $VIRTUAL_ENV"
    PIP_CMD="$VIRTUAL_ENV/bin/pip"
    PYTHON_CMD="$VIRTUAL_ENV/bin/python"
else
    PIP_CMD="pip"
    PYTHON_CMD="python"
fi

echo "Installing PyJWT..."
$PIP_CMD install PyJWT==2.8.0

echo ""
echo "Verifying installation..."
$PYTHON_CMD -c "import jwt; print(f'✅ PyJWT installed: {jwt.__version__}')"

echo ""
echo "✅ JWT import fix complete!"
echo ""
echo "If running in Docker, rebuild the image:"
echo "  docker-compose build"
echo "  or"
echo "  docker build -t gateway-service ."
