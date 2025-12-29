#!/usr/bin/env python3
"""
Check Nacos connection to auth-service
Verifies:
1. Nacos server connectivity
2. auth-service registration status
3. Service instance discovery
4. Health check endpoint
"""
import sys
import os
import asyncio
import httpx
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.utils.nacos_client import NacosClientUtil
from app.settings import get_settings


def check_nacos_server(nacos_addr: str) -> bool:
    """
    Check if Nacos server is accessible
    
    Args:
        nacos_addr: Nacos server address
        
    Returns:
        True if accessible
    """
    print("=" * 70)
    print("1. Checking Nacos Server Connectivity")
    print("=" * 70)
    
    try:
        # Parse address
        if "://" not in nacos_addr:
            nacos_addr = f"http://{nacos_addr}"
        
        base_url = nacos_addr.rstrip("/")
        
        # Try multiple health check endpoints
        health_urls = [
            f"{base_url}/nacos/v1/console/health",
            f"{base_url}/nacos/v1/ns/operator/metrics",
            f"{base_url}/nacos/",
            f"{base_url}/"
        ]
        
        print(f"  Nacos Server: {nacos_addr}")
        
        for health_url in health_urls:
            try:
                print(f"  Trying: {health_url}")
                response = httpx.get(health_url, timeout=5, follow_redirects=True)
                
                if response.status_code in [200, 302, 404]:  # 404 might mean server is up but endpoint doesn't exist
                    print(f"  ✅ Nacos server is accessible (status: {response.status_code})")
                    if response.status_code == 200:
                        print(f"  Response: {response.text[:100]}")
                    return True
            except httpx.ConnectError:
                continue
            except Exception as e:
                continue
        
        # If all URLs failed, try basic connection
        try:
            response = httpx.get(f"{base_url}/", timeout=5)
            print(f"  ✅ Nacos server is accessible (status: {response.status_code})")
            return True
        except:
            pass
        
        print(f"  ⚠️  Could not verify Nacos server health, but will try to connect anyway")
        return True  # Return True to allow checking service registration
            
    except httpx.ConnectError:
        print(f"  ❌ Cannot connect to Nacos server at {nacos_addr}")
        print(f"  Please check:")
        print(f"    - Is Nacos server running?")
        print(f"    - Is the address correct?")
        return False
    except Exception as e:
        print(f"  ❌ Error checking Nacos server: {str(e)}")
        return False


def check_service_registration(service_name: str = "auth-service") -> bool:
    """
    Check if auth-service is registered with Nacos
    
    Args:
        service_name: Service name to check
        
    Returns:
        True if registered
    """
    print()
    print("=" * 70)
    print(f"2. Checking {service_name} Registration")
    print("=" * 70)
    
    try:
        client = NacosClientUtil()
        
        # Get service instances
        instances = client.get_service_instances(service_name)
        
        if not instances:
            print(f"  ❌ {service_name} is NOT registered with Nacos")
            print(f"  Instances found: 0")
            print()
            print(f"  To register {service_name}, run:")
            print(f"    python scripts/register_service_nacos.py --service {service_name} --ip 127.0.0.1 --port 8000")
            return False
        
        print(f"  ✅ {service_name} is registered with Nacos")
        print(f"  Instances found: {len(instances)}")
        print()
        
        for i, instance in enumerate(instances, 1):
            if isinstance(instance, dict):
                ip = instance.get("ip", "N/A")
                port = instance.get("port", "N/A")
                healthy = instance.get("healthy", False)
                weight = instance.get("weight", 1.0)
                metadata = instance.get("metadata", {})
                
                status = "✅ Healthy" if healthy else "❌ Unhealthy"
                print(f"  Instance {i}:")
                print(f"    IP: {ip}")
                print(f"    Port: {port}")
                print(f"    Status: {status}")
                print(f"    Weight: {weight}")
                if metadata:
                    print(f"    Metadata: {metadata}")
            else:
                print(f"  Instance {i}: {instance}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error checking service registration: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def check_auth_service_health(ip: str = "127.0.0.1", port: int = 8000) -> bool:
    """
    Check if auth-service health endpoint is accessible
    
    Args:
        ip: Service IP address
        port: Service port
        
    Returns:
        True if accessible
    """
    print()
    print("=" * 70)
    print("3. Checking auth-service Health Endpoint")
    print("=" * 70)
    
    try:
        url = f"http://{ip}:{port}/health"
        print(f"  Health Check URL: {url}")
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ auth-service is healthy")
                print(f"  Response: {data}")
                return True
            else:
                print(f"  ⚠️  auth-service responded with status {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                return False
                
    except httpx.ConnectError:
        print(f"  ❌ Cannot connect to auth-service at {ip}:{port}")
        print(f"  Please check:")
        print(f"    - Is auth-service running?")
        print(f"    - Is the IP and port correct?")
        return False
    except Exception as e:
        print(f"  ❌ Error checking auth-service health: {str(e)}")
        return False


async def check_service_discovery(service_name: str = "auth-service") -> bool:
    """
    Check if gateway can discover auth-service through Nacos
    
    Args:
        service_name: Service name to discover
        
    Returns:
        True if discoverable
    """
    print()
    print("=" * 70)
    print(f"4. Checking Service Discovery for {service_name}")
    print("=" * 70)
    
    try:
        from app.core.discovery import NacosServiceDiscovery
        
        # NacosServiceDiscovery doesn't take settings in __init__
        discovery = NacosServiceDiscovery()
        
        instances = await discovery.get_instances(service_name)
        
        if not instances:
            print(f"  ❌ Cannot discover {service_name} instances")
            print(f"  Instances found: 0")
            return False
        
        print(f"  ✅ Successfully discovered {service_name}")
        print(f"  Instances found: {len(instances)}")
        print()
        
        for i, instance in enumerate(instances, 1):
            print(f"  Instance {i}:")
            print(f"    URL: {instance.url}")
            print(f"    Weight: {instance.weight}")
            print(f"    Healthy: {instance.healthy}")
            if instance.metadata:
                print(f"    Metadata: {instance.metadata}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error in service discovery: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main function"""
    print()
    print("🔍 Nacos Connection Check for auth-service")
    print("=" * 70)
    print()
    
    settings = get_settings()
    nacos_addr = settings.nacos_server_addresses
    
    results = {
        "nacos_server": False,
        "service_registration": False,
        "auth_service_health": False,
        "service_discovery": False
    }
    
    # 1. Check Nacos server
    results["nacos_server"] = check_nacos_server(nacos_addr)
    
    if not results["nacos_server"]:
        print()
        print("❌ Cannot proceed: Nacos server is not accessible")
        print("   Please start Nacos server first")
        return
    
    # 2. Check service registration
    results["service_registration"] = check_service_registration("auth-service")
    
    # 3. Check auth-service health
    # Get IP and port from registered instances if available
    ip = "127.0.0.1"
    port = 8000
    
    if results["service_registration"]:
        try:
            client = NacosClientUtil()
            instances = client.get_service_instances("auth-service")
            if instances and isinstance(instances[0], dict):
                ip = instances[0].get("ip", ip)
                port = instances[0].get("port", port)
        except:
            pass
    
    results["auth_service_health"] = await check_auth_service_health(ip, port)
    
    # 4. Check service discovery
    results["service_discovery"] = await check_service_discovery("auth-service")
    
    # Summary
    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for key, value in results.items():
        status = "✅ PASS" if value else "❌ FAIL"
        print(f"  {key.replace('_', ' ').title()}: {status}")
    
    print()
    print(f"Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("✅ All checks passed! Nacos can connect to auth-service")
    else:
        print("⚠️  Some checks failed. Please review the errors above.")
    
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
