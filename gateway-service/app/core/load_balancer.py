"""
Load balancing strategies for service instances
"""

import random
from typing import List, Optional
from enum import Enum
from app.core.discovery import ServiceInstance
from app.settings import get_settings


class LoadBalancingStrategy(str, Enum):
    """Load balancing strategy types"""
    
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    RANDOM = "random"


class LoadBalancer:
    """Load balancer for distributing requests across service instances"""
    
    def __init__(self, strategy: Optional[str] = None):
        """
        Initialize load balancer
        
        Args:
            strategy: Load balancing strategy
        """
        self.settings = get_settings()
        self.strategy = strategy or self.settings.load_balancer_strategy
        self.round_robin_counters: dict[str, int] = {}
        self.connection_counts: dict[str, int] = {}
    
    def select_instance(self, instances: List[ServiceInstance], service_name: str) -> Optional[ServiceInstance]:
        """
        Select service instance based on strategy
        
        Args:
            instances: List of available service instances
            service_name: Name of the service
            
        Returns:
            Selected service instance or None
        """
        # Filter healthy instances
        healthy_instances = [inst for inst in instances if inst.healthy]
        
        if not healthy_instances:
            return None
        
        if len(healthy_instances) == 1:
            return healthy_instances[0]
        
        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._round_robin(healthy_instances, service_name)
        elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return self._least_connections(healthy_instances, service_name)
        elif self.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin(healthy_instances, service_name)
        elif self.strategy == LoadBalancingStrategy.RANDOM:
            return self._random(healthy_instances)
        else:
            return self._round_robin(healthy_instances, service_name)
    
    def _round_robin(self, instances: List[ServiceInstance], service_name: str) -> ServiceInstance:
        """
        Round-robin selection
        
        Args:
            instances: List of service instances
            service_name: Name of the service
            
        Returns:
            Selected instance
        """
        if service_name not in self.round_robin_counters:
            self.round_robin_counters[service_name] = 0
        
        index = self.round_robin_counters[service_name] % len(instances)
        self.round_robin_counters[service_name] += 1
        
        return instances[index]
    
    def _least_connections(self, instances: List[ServiceInstance], service_name: str) -> ServiceInstance:
        """
        Least connections selection
        
        Args:
            instances: List of service instances
            service_name: Name of the service
            
        Returns:
            Selected instance
        """
        if service_name not in self.connection_counts:
            self.connection_counts[service_name] = {inst.url: 0 for inst in instances}
        
        counts = self.connection_counts[service_name]
        selected = min(instances, key=lambda inst: counts.get(inst.url, 0))
        counts[selected.url] = counts.get(selected.url, 0) + 1
        
        return selected
    
    def _weighted_round_robin(self, instances: List[ServiceInstance], service_name: str) -> ServiceInstance:
        """
        Weighted round-robin selection
        
        Args:
            instances: List of service instances
            service_name: Name of the service
            
        Returns:
            Selected instance
        """
        total_weight = sum(inst.weight for inst in instances)
        if total_weight == 0:
            return self._round_robin(instances, service_name)
        
        if service_name not in self.round_robin_counters:
            self.round_robin_counters[service_name] = 0
        
        current = self.round_robin_counters[service_name] % total_weight
        self.round_robin_counters[service_name] += 1
        
        cumulative = 0
        for instance in instances:
            cumulative += instance.weight
            if current < cumulative:
                return instance
        
        return instances[0]
    
    def _random(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """
        Random selection
        
        Args:
            instances: List of service instances
            
        Returns:
            Selected instance
        """
        return random.choice(instances)
    
    def release_connection(self, service_name: str, instance_url: str) -> None:
        """
        Release connection count for instance
        
        Args:
            service_name: Name of the service
            instance_url: URL of the instance
        """
        if service_name in self.connection_counts:
            if instance_url in self.connection_counts[service_name]:
                count = self.connection_counts[service_name][instance_url]
                if count > 0:
                    self.connection_counts[service_name][instance_url] = count - 1

