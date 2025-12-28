#!/usr/bin/env python3
"""
Test script for HashiCorp Vault integration
Tests Vault connection, authentication, and secret retrieval using .env.dev configuration
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment from .env.dev
try:
    from dotenv import load_dotenv
    env_file = project_root / ".env.dev"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ Loaded environment from: {env_file}")
    else:
        print(f"⚠️  .env.dev file not found at: {env_file}")
        print("   Using system environment variables only")
except ImportError:
    print("⚠️  python-dotenv not installed, using system environment variables only")

print("=" * 70)
print("Vault Integration Test")
print("=" * 70)
print()

# Check Vault configuration
print("📋 Vault Configuration:")
print("-" * 70)
vault_addr = os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
vault_auth_method = os.getenv("VAULT_AUTH_METHOD", "approle")
jwt_vault_hs256_path = os.getenv("JWT_VAULT_HS256_PATH", "secret/jwt/hs256")
jwt_vault_rs256_path = os.getenv("JWT_VAULT_RS256_PATH", "secret/jwt/rs256")

print(f"  VAULT_ADDR: {vault_addr}")
print(f"  VAULT_AUTH_METHOD: {vault_auth_method}")
print(f"  JWT_VAULT_HS256_PATH: {jwt_vault_hs256_path}")
print(f"  JWT_VAULT_RS256_PATH: {jwt_vault_rs256_path}")

if vault_auth_method == "approle":
    role_id = os.getenv("VAULT_ROLE_ID")
    secret_id = os.getenv("VAULT_SECRET_ID")
    print(f"  VAULT_ROLE_ID: {'✅ Set' if role_id else '❌ Not set'}")
    print(f"  VAULT_SECRET_ID: {'✅ Set' if secret_id else '❌ Not set'}")
elif vault_auth_method == "token":
    vault_token = os.getenv("VAULT_TOKEN")
    print(f"  VAULT_TOKEN: {'✅ Set' if vault_token else '❌ Not set'}")

print()
print("=" * 70)
print()

# Test Vault connection
print("🔌 Testing Vault Connection...")
print("-" * 70)

try:
    from app.utils.vault_util import VaultUtil
    
    # Initialize Vault client
    print("1. Initializing Vault client...")
    vault_util = VaultUtil()
    print("   ✅ Vault client initialized")
    
    # Check connection
    print("2. Checking Vault connection...")
    if vault_util.is_connected():
        print("   ✅ Connected and authenticated")
    else:
        print("   ❌ Not connected")
        sys.exit(1)
    
    # Health check
    print("3. Checking Vault health...")
    health = vault_util.health_check()
    print(f"   Status: {health.get('status', 'unknown')}")
    if health.get('sealed'):
        print("   ⚠️  Vault is sealed")
    if health.get('version'):
        print(f"   Version: {health.get('version')}")
    
    print()
    print("=" * 70)
    print()
    
    # Test reading secrets
    print("🔐 Testing Secret Retrieval...")
    print("-" * 70)
    
    # Test JWT HS256 secret
    print(f"4. Reading JWT HS256 secret from: {jwt_vault_hs256_path}")
    try:
        jwt_secret_hs256 = vault_util.get_jwt_secret("HS256")
        print(f"   ✅ Secret retrieved (length: {len(jwt_secret_hs256)} chars)")
        print(f"   Preview: {jwt_secret_hs256[:20]}..." if len(jwt_secret_hs256) > 20 else f"   Value: {jwt_secret_hs256}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test JWT RS256 secret (if path is configured)
    if jwt_vault_rs256_path:
        print(f"5. Reading JWT RS256 secret from: {jwt_vault_rs256_path}")
        try:
            jwt_secret_rs256 = vault_util.get_jwt_secret("RS256")
            print(f"   ✅ Secret retrieved (length: {len(jwt_secret_rs256)} chars)")
            print(f"   Preview: {jwt_secret_rs256[:50]}..." if len(jwt_secret_rs256) > 50 else f"   Value: {jwt_secret_rs256[:100]}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    # Test reading raw secret
    print(f"6. Reading raw secret from: {jwt_vault_hs256_path}")
    try:
        secret_data = vault_util.read_secret(jwt_vault_hs256_path)
        print(f"   ✅ Raw secret data retrieved")
        print(f"   Keys: {list(secret_data.keys())}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    print()
    print("=" * 70)
    print("✅ All Vault tests completed successfully!")
    print("=" * 70)
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print()
    print("💡 Solution: Install hvac library")
    print("   pip install hvac")
    sys.exit(1)
    
except ConnectionError as e:
    error_msg = str(e)
    print(f"❌ Connection Error: {e}")
    print()
    if "sealed" in error_msg.lower():
        print("💡 Vault is sealed. To unseal Vault:")
        print("   1. Start Vault server: vault server -dev (for development)")
        print("   2. Or unseal existing Vault: vault operator unseal <unseal-key>")
        print("   3. For development, you can use: vault operator unseal -address=http://127.0.0.1:8200")
    else:
        print("💡 Troubleshooting:")
        print("   1. Check if Vault is running: curl http://127.0.0.1:8200/v1/sys/health")
        print("   2. Verify VAULT_ADDR in .env.dev")
        print("   3. Check VAULT_ROLE_ID and VAULT_SECRET_ID are correct")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
