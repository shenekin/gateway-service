#!/usr/bin/env python3
"""Quick fix script for JWT import error"""
import sys
import subprocess

print('🔧 Fixing JWT Import Error')
print('=' * 70)
print()

# Install PyJWT
print('Installing PyJWT==2.8.0...')
result = subprocess.run(
    [sys.executable, '-m', 'pip', 'install', 'PyJWT==2.8.0'],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print('✅ PyJWT installed successfully')
else:
    print(f'❌ Installation failed: {result.stderr}')
    sys.exit(1)

# Verify
print()
print('Verifying installation...')
try:
    import jwt
    print(f'✅ JWT module available: {jwt.__version__}')
    print()
    print('✅ Fix complete! You can now run: python run.py')
except ImportError as e:
    print(f'❌ Verification failed: {e}')
    sys.exit(1)
