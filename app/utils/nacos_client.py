"""
Nacos client utility for service registration and discovery
"""
import os
import json
from typing import List, Optional, Dict, Any
from nacos import NacosClient
from app.settings import get_settings


class NacosClientUtil:
    """Utility class for Nacos operations"""
    
    def __init__(self, server_addresses: Optional[str] = None, 
                 namespace: Optional[str] = None,
                 username: Optional[str] = None,
                 password: Optional[str] = None):
        """
        Initialize Nacos client
        
        Args:
            server_addresses: Nacos server addresses (comma-separated)
            namespace: Nacos namespace
            username: Nacos username (optional)
            password: Nacos password (optional)
        """
        settings = get_settings()
        
        self.server_addresses = server_addresses or settings.nacos_server_addresses
        self.namespace = namespace or settings.nacos_namespace
        self.username = username or os.getenv("NACOS_USERNAME")
        self.password = password or os.getenv("NACOS_PASSWORD")
        
        # Parse server addresses
        servers = []
        for addr in self.server_addresses.split(","):
            addr = addr.strip()
            if "://" not in addr:
                addr = f"http://{addr}"
            servers.append(addr)
        
        # Initialize Nacos client
        self.client = NacosClient(
            server_addresses=",".join(servers),
            namespace=self.namespace,
            username=self.username,
            password=self.password
        )
    
    def register_service(self, 
                        service_name: str,
                        ip: str,
                        port: int,
                        group_name: str = "DEFAULT_GROUP",
                        weight: float = 1.0,
                        metadata: Optional[Dict[str, Any]] = None,
                        healthy: bool = True,
                        enabled: bool = True,
                        ephemeral: bool = True,
                        cluster_name: Optional[str] = None,
                        heartbeat_interval: Optional[int] = None) -> bool:
        """
        Register service instance with Nacos
        
        Args:
            service_name: Service name
            ip: Service IP address
            port: Service port
            group_name: Service group name
            weight: Instance weight for load balancing
            metadata: Additional metadata
            healthy: Health status
            enabled: Whether instance is enabled
            ephemeral: Whether instance is ephemeral (auto-deregister on disconnect)
            cluster_name: Cluster name (optional)
            heartbeat_interval: Heartbeat interval in seconds (optional)
            
        Returns:
            True if successful
        """
        try:
            metadata = metadata or {}
            metadata_str = json.dumps(metadata) if metadata else ""
            
            # NacosClient uses 'enable' not 'enabled'
            result = self.client.add_naming_instance(
                service_name=service_name,
                ip=ip,
                port=port,
                group_name=group_name,
                weight=weight,
                metadata=metadata_str,
                healthy=healthy,
                enable=enabled,  # Fixed: use 'enable' not 'enabled'
                ephemeral=ephemeral,
                cluster_name=cluster_name,
                heartbeat_interval=heartbeat_interval
            )
            
            return result
        except Exception as e:
            print(f"Failed to register service {service_name}: {str(e)}")
            return False
    
    def deregister_service(self,
                          service_name: str,
                          ip: str,
                          port: int,
                          group_name: str = "DEFAULT_GROUP") -> bool:
        """
        Deregister service instance from Nacos
        
        Args:
            service_name: Service name
            ip: Service IP address
            port: Service port
            group_name: Service group name
            
        Returns:
            True if successful
        """
        try:
            result = self.client.remove_naming_instance(
                service_name=service_name,
                ip=ip,
                port=port,
                group_name=group_name
            )
            return result
        except Exception as e:
            print(f"Failed to deregister service {service_name}: {str(e)}")
            return False
    
    def get_service_instances(self,
                              service_name: str,
                              group_name: str = "DEFAULT_GROUP",
                              healthy_only: bool = False) -> List[Dict[str, Any]]:
        """
        Get service instances from Nacos
        
        Args:
            service_name: Service name
            group_name: Service group name
            healthy_only: Only return healthy instances
            
        Returns:
            List of service instances
        """
        try:
            # list_naming_instance returns a dict with 'hosts' key containing the instances
            response = self.client.list_naming_instance(
                service_name=service_name,
                group_name=group_name
            )
            
            # Extract hosts from response
            if isinstance(response, dict):
                instances = response.get("hosts", [])
            elif isinstance(response, list):
                instances = response
            else:
                instances = []
            
            # Filter healthy instances if requested
            if healthy_only:
                instances = [inst for inst in instances if isinstance(inst, dict) and inst.get("healthy", True)]
            
            return instances
        except Exception as e:
            print(f"Failed to get service instances for {service_name}: {str(e)}")
            return []
    
    def send_heartbeat(self,
                      service_name: str,
                      ip: str,
                      port: int,
                      group_name: str = "DEFAULT_GROUP",
                      weight: float = 1.0,
                      metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Send heartbeat to Nacos
        
        Args:
            service_name: Service name
            ip: Service IP address
            port: Service port
            group_name: Service group name
            weight: Instance weight
            metadata: Additional metadata
            
        Returns:
            True if successful
        """
        try:
            metadata = metadata or {}
            metadata_str = json.dumps(metadata) if metadata else ""
            
            result = self.client.send_heartbeat(
                service_name=service_name,
                ip=ip,
                port=port,
                group_name=group_name,
                weight=weight,
                metadata=metadata_str
            )
            return result
        except Exception as e:
            print(f"Failed to send heartbeat for {service_name}: {str(e)}")
            return False
