#!/usr/bin/env python3
"""
Register microservices with Nacos service discovery
Supports registering multiple services at once
"""
import sys
import os
import argparse
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.utils.nacos_client import NacosClientUtil


def register_service(service_name: str, ip: str, port: int, 
                    group_name: str = "DEFAULT_GROUP",
                    weight: float = 1.0,
                    metadata: dict = None,
                    nacos_addr: str = None,
                    namespace: str = None):
    """
    Register a single service with Nacos
    
    Args:
        service_name: Service name
        ip: Service IP address
        port: Service port
        group_name: Service group name
        weight: Instance weight
        metadata: Additional metadata
        nacos_addr: Nacos server address
        namespace: Nacos namespace
    """
    try:
        client = NacosClientUtil(
            server_addresses=nacos_addr,
            namespace=namespace
        )
        
        result = client.register_service(
            service_name=service_name,
            ip=ip,
            port=port,
            group_name=group_name,
            weight=weight,
            metadata=metadata
        )
        
        if result:
            print(f"✅ Successfully registered {service_name} at {ip}:{port}")
            return True
        else:
            print(f"❌ Failed to register {service_name}")
            return False
    except Exception as e:
        print(f"❌ Error registering {service_name}: {str(e)}")
        return False


def register_from_config(config_file: str):
    """
    Register multiple services from configuration file
    
    Args:
        config_file: Path to JSON configuration file
    """
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        nacos_addr = config.get("nacos_server", "localhost:8848")
        namespace = config.get("namespace", "public")
        group_name = config.get("group", "DEFAULT_GROUP")
        
        services = config.get("services", [])
        
        print("=" * 70)
        print("Registering Services with Nacos")
        print("=" * 70)
        print(f"Nacos Server: {nacos_addr}")
        print(f"Namespace: {namespace}")
        print(f"Group: {group_name}")
        print(f"Services: {len(services)}")
        print()
        
        success_count = 0
        for service in services:
            service_name = service.get("name")
            ip = service.get("ip", "127.0.0.1")
            port = service.get("port")
            weight = service.get("weight", 1.0)
            metadata = service.get("metadata", {})
            
            if not service_name or not port:
                print(f"⚠️  Skipping invalid service config: {service}")
                continue
            
            if register_service(
                service_name=service_name,
                ip=ip,
                port=port,
                group_name=group_name,
                weight=weight,
                metadata=metadata,
                nacos_addr=nacos_addr,
                namespace=namespace
            ):
                success_count += 1
        
        print()
        print("=" * 70)
        print(f"Registration Summary: {success_count}/{len(services)} services registered")
        print("=" * 70)
        
        return success_count == len(services)
    except Exception as e:
        print(f"❌ Error reading config file: {str(e)}")
        return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Register services with Nacos")
    parser.add_argument("--service", type=str, help="Service name")
    parser.add_argument("--ip", type=str, default="127.0.0.1", help="Service IP address")
    parser.add_argument("--port", type=int, help="Service port")
    parser.add_argument("--group", type=str, default="DEFAULT_GROUP", help="Service group")
    parser.add_argument("--weight", type=float, default=1.0, help="Instance weight")
    parser.add_argument("--metadata", type=str, help="Metadata as JSON string")
    parser.add_argument("--nacos", type=str, help="Nacos server address (default: from .env)")
    parser.add_argument("--namespace", type=str, help="Nacos namespace (default: from .env)")
    parser.add_argument("--config", type=str, help="Path to JSON config file for multiple services")
    
    args = parser.parse_args()
    
    # Load Nacos settings from environment
    from app.settings import get_settings
    settings = get_settings()
    
    nacos_addr = args.nacos or settings.nacos_server_addresses
    namespace = args.namespace or settings.nacos_namespace
    
    # Register from config file
    if args.config:
        success = register_from_config(args.config)
        sys.exit(0 if success else 1)
    
    # Register single service
    if not args.service or not args.port:
        parser.print_help()
        print("\n❌ Error: --service and --port are required for single service registration")
        sys.exit(1)
    
    metadata = {}
    if args.metadata:
        try:
            metadata = json.loads(args.metadata)
        except:
            print(f"⚠️  Warning: Invalid metadata JSON, ignoring: {args.metadata}")
    
    success = register_service(
        service_name=args.service,
        ip=args.ip,
        port=args.port,
        group_name=args.group,
        weight=args.weight,
        metadata=metadata,
        nacos_addr=nacos_addr,
        namespace=namespace
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
