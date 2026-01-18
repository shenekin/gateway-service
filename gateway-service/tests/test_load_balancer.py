"""
Unit tests for load balancer module
"""

import pytest
from app.core.load_balancer import LoadBalancer, LoadBalancingStrategy
from app.core.discovery import ServiceInstance


def test_load_balancer_round_robin():
    """Test round-robin load balancing"""
    instances = [
        ServiceInstance("http://service1:8000"),
        ServiceInstance("http://service2:8000"),
        ServiceInstance("http://service3:8000")
    ]
    
    lb = LoadBalancer(strategy=LoadBalancingStrategy.ROUND_ROBIN)
    
    selected1 = lb.select_instance(instances, "test-service")
    selected2 = lb.select_instance(instances, "test-service")
    selected3 = lb.select_instance(instances, "test-service")
    
    assert selected1.url != selected2.url or selected2.url != selected3.url


def test_load_balancer_least_connections():
    """Test least connections load balancing"""
    instances = [
        ServiceInstance("http://service1:8000"),
        ServiceInstance("http://service2:8000")
    ]
    
    lb = LoadBalancer(strategy=LoadBalancingStrategy.LEAST_CONNECTIONS)
    
    selected = lb.select_instance(instances, "test-service")
    assert selected is not None
    assert selected in instances


def test_load_balancer_weighted():
    """Test weighted round-robin load balancing"""
    instances = [
        ServiceInstance("http://service1:8000", weight=3),
        ServiceInstance("http://service2:8000", weight=1)
    ]
    
    lb = LoadBalancer(strategy=LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN)
    
    selected = lb.select_instance(instances, "test-service")
    assert selected is not None


def test_load_balancer_single_instance():
    """Test load balancer with single instance"""
    instances = [ServiceInstance("http://service1:8000")]
    
    lb = LoadBalancer()
    selected = lb.select_instance(instances, "test-service")
    
    assert selected.url == "http://service1:8000"


def test_load_balancer_no_healthy_instances():
    """Test load balancer with no healthy instances"""
    instances = [
        ServiceInstance("http://service1:8000", healthy=False),
        ServiceInstance("http://service2:8000", healthy=False)
    ]
    
    lb = LoadBalancer()
    selected = lb.select_instance(instances, "test-service")
    
    assert selected is None

