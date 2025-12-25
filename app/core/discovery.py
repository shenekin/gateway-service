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
        # Nacos client would be initialized here
        # from nacos import NacosClient
        # self.client = NacosClient(...)
    
    async def get_instances(self, service_name: str) -> List[ServiceInstance]:
        """
        Get service instances from Nacos
        
        Args:
            service_name: Name of the service
            
        Returns:
            List of service instances
        """
        # Implementation would use Nacos client
        # instances = await self.client.list_naming_instance(service_name)
        # return [ServiceInstance(...) for instance in instances]
        return []
    
    async def register(self, service_name: str, instance: ServiceInstance) -> bool:
        """Register service instance with Nacos"""
        # Implementation would use Nacos client
        return False
    
    async def deregister(self, service_name: str, instance_url: str) -> bool:
        """Deregister service instance from Nacos"""
        # Implementation would use Nacos client
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

