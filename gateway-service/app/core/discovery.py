"""
Service discovery implementation for Nacos, Consul, and etcd
"""

import asyncio
import yaml
from typing import List, Optional, Dict
from pathlib import Path
from abc import ABC, abstractmethod
from app.settings import get_settings


class ServiceInstance:
    """Service instance representation"""
    
    def __init__(self, url: str, weight: int = 1, healthy: bool = True, metadata: Optional[Dict] = None):
        """
        Initialize service instance
        
        Args:
            url: Service instance URL
            weight: Load balancing weight
            healthy: Health status
            metadata: Additional metadata
        """
        self.url = url
        self.weight = weight
        self.healthy = healthy
        self.metadata = metadata or {}
        self.failure_count = 0
        self.last_health_check = None


class ServiceDiscovery(ABC):
    """Abstract service discovery interface"""
    
    @abstractmethod
    async def get_instances(self, service_name: str) -> List[ServiceInstance]:
        """
        Get service instances
        
        Args:
            service_name: Name of the service
            
        Returns:
            List of service instances
        """
        pass
    
    @abstractmethod
    async def register(self, service_name: str, instance: ServiceInstance) -> bool:
        """
        Register service instance
        
        Args:
            service_name: Name of the service
            instance: Service instance to register
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def deregister(self, service_name: str, instance_url: str) -> bool:
        """
        Deregister service instance
        
        Args:
            service_name: Name of the service
            instance_url: URL of instance to deregister
            
        Returns:
            True if successful
        """
        pass


class StaticServiceDiscovery(ServiceDiscovery):
    """Static service discovery from configuration file"""
    
    def __init__(self, services_file: Optional[str] = None):
        """
        Initialize static service discovery
        
        Args:
            services_file: Path to services configuration file
        """
        self.settings = get_settings()
        self.services_file = services_file or "config/services.yaml"
        self.services: Dict[str, List[ServiceInstance]] = {}
        self._load_services()
    
    def _load_services(self) -> None:
        """Load services from configuration file"""
        try:
            services_path = Path(self.services_file)
            if not services_path.exists():
                services_path = Path(__file__).parent.parent.parent / self.services_file
            
            with open(services_path, "r") as f:
                config = yaml.safe_load(f)
            
            services_data = config.get("services", {})
            for service_name, service_config in services_data.items():
                instances = []
                for instance_data in service_config.get("instances", []):
                    instance = ServiceInstance(
                        url=instance_data["url"],
                        weight=instance_data.get("weight", 1),
                        healthy=instance_data.get("healthy", True)
                    )
                    instances.append(instance)
                self.services[service_name] = instances
        except Exception as e:
            raise RuntimeError(f"Failed to load services: {e}")
    
    async def get_instances(self, service_name: str) -> List[ServiceInstance]:
        """
        Get service instances
        
        Args:
            service_name: Name of the service
            
        Returns:
            List of service instances
        """
        return self.services.get(service_name, [])
    
    async def register(self, service_name: str, instance: ServiceInstance) -> bool:
        """
        Register service instance (not supported in static mode)
        
        Args:
            service_name: Name of the service
            instance: Service instance to register
            
        Returns:
            False (not supported)
        """
        return False
    
    async def deregister(self, service_name: str, instance_url: str) -> bool:
        """
        Deregister service instance (not supported in static mode)
        
        Args:
            service_name: Name of the service
            instance_url: URL of instance to deregister
            
        Returns:
            False (not supported)
        """
        return False
    
    def reload_services(self) -> None:
        """Reload services from configuration file"""
        self.services.clear()
        self._load_services()


class NacosServiceDiscovery(ServiceDiscovery):
    """Nacos service discovery implementation"""
    
    def __init__(self):
        """Initialize Nacos service discovery"""
        self.settings = get_settings()
        from app.utils.nacos_client import NacosClientUtil
        
        self.nacos_client = NacosClientUtil(
            server_addresses=self.settings.nacos_server_addresses,
            namespace=self.settings.nacos_namespace
        )
    
    async def get_instances(self, service_name: str) -> List[ServiceInstance]:
        """
        Get service instances from Nacos
        
        Args:
            service_name: Name of the service
            
        Returns:
            List of service instances
        """
        try:
            instances_data = self.nacos_client.get_service_instances(
                service_name=service_name,
                group_name=self.settings.nacos_group,
                healthy_only=True
            )
            
            instances = []
            for inst_data in instances_data:
                # Ensure inst_data is a dictionary
                if not isinstance(inst_data, dict):
                    continue
                
                # Parse instance data
                ip = inst_data.get("ip", "")
                port = inst_data.get("port", 0)
                weight = inst_data.get("weight", 1.0)
                healthy = inst_data.get("healthy", True)
                metadata = inst_data.get("metadata", {})
                
                # Build URL
                if isinstance(metadata, str):
                    import json
                    try:
                        metadata = json.loads(metadata)
                    except:
                        metadata = {}
                elif not isinstance(metadata, dict):
                    metadata = {}
                
                # Use metadata URL if available, otherwise construct from IP:port
                url = metadata.get("url") if isinstance(metadata, dict) else None
                if not url:
                    url = f"http://{ip}:{port}"
                
                instance = ServiceInstance(
                    url=url,
                    weight=weight,
                    healthy=healthy,
                    metadata=metadata if isinstance(metadata, dict) else {}
                )
                instances.append(instance)
            
            return instances
        except Exception as e:
            # Log error but return empty list
            print(f"Error getting instances from Nacos: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    async def register(self, service_name: str, instance: ServiceInstance) -> bool:
        """
        Register service instance with Nacos
        
        Args:
            service_name: Name of the service
            instance: Service instance to register
            
        Returns:
            True if successful
        """
        try:
            # Parse URL to get IP and port
            from urllib.parse import urlparse
            parsed = urlparse(instance.url)
            ip = parsed.hostname or "127.0.0.1"
            port = parsed.port or 8000
            
            return self.nacos_client.register_service(
                service_name=service_name,
                ip=ip,
                port=port,
                group_name=self.settings.nacos_group,
                weight=instance.weight,
                metadata=instance.metadata,
                healthy=instance.healthy
            )
        except Exception as e:
            print(f"Error registering service with Nacos: {str(e)}")
            return False
    
    async def deregister(self, service_name: str, instance_url: str) -> bool:
        """
        Deregister service instance from Nacos
        
        Args:
            service_name: Name of the service
            instance_url: URL of instance to deregister
            
        Returns:
            True if successful
        """
        try:
            from urllib.parse import urlparse
            parsed = urlparse(instance_url)
            ip = parsed.hostname or "127.0.0.1"
            port = parsed.port or 8000
            
            return self.nacos_client.deregister_service(
                service_name=service_name,
                ip=ip,
                port=port,
                group_name=self.settings.nacos_group
            )
        except Exception as e:
            print(f"Error deregistering service from Nacos: {str(e)}")
            return False


def create_service_discovery() -> ServiceDiscovery:
    """
    Create service discovery instance based on configuration
    
    Returns:
        Service discovery instance
    """
    settings = get_settings()
    
    if settings.service_discovery_type == "nacos":
        return NacosServiceDiscovery()
    else:
        return StaticServiceDiscovery()

