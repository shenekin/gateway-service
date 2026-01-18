#!/usr/bin/env python3
"""
Reload gateway service discovery configuration
This script can be used to reload services without restarting the gateway
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.discovery import StaticServiceDiscovery
import asyncio

async def reload_and_check():
    """Reload service discovery and check auth-service"""
    discovery = StaticServiceDiscovery()
    
    # Reload services
    discovery.reload_services()
    
    # Check auth-service
    instances = await discovery.get_instances('auth-service')
    
    print("=" * 70)
    print("Service Discovery Reload")
    print("=" * 70)
    print()
    print(f"Auth Service Instances: {len(instances)}")
    for inst in instances:
        print(f"  ✅ {inst.url}")
        print(f"     Healthy: {inst.healthy}")
        print(f"     Weight: {inst.weight}")
    print()
    
    if len(instances) == 0:
        print("❌ No instances found! Check config/services.yaml")
        return False
    else:
        print("✅ Service discovery reloaded successfully")
        return True

if __name__ == "__main__":
    success = asyncio.run(reload_and_check())
    sys.exit(0 if success else 1)
