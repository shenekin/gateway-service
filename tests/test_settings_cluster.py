"""
Unit tests for cluster configuration in settings
"""

import os
import pytest
from app.settings import Settings, get_settings, reload_settings


class TestSettingsClusterConfiguration:
    """Test cases for cluster configuration features"""
    
    def test_deployment_mode_default(self):
        """Test default deployment mode is single"""
        settings = get_settings()
        assert settings.deployment_mode == "single"
        assert settings.is_single_instance_mode is True
        assert settings.is_cluster_mode is False
    
    def test_deployment_mode_cluster(self):
        """Test cluster deployment mode"""
        original_mode = os.getenv("DEPLOYMENT_MODE")
        
        try:
            os.environ["DEPLOYMENT_MODE"] = "cluster"
            settings = reload_settings()
            
            assert settings.deployment_mode == "cluster"
            assert settings.is_cluster_mode is True
            assert settings.is_single_instance_mode is False
        finally:
            if original_mode:
                os.environ["DEPLOYMENT_MODE"] = original_mode
            else:
                os.environ.pop("DEPLOYMENT_MODE", None)
    
    def test_cluster_enabled_flag(self):
        """Test cluster_enabled flag"""
        original_flag = os.getenv("CLUSTER_ENABLED")
        
        try:
            os.environ["CLUSTER_ENABLED"] = "true"
            settings = reload_settings()
            
            assert settings.cluster_enabled is True
            assert settings.is_cluster_mode is True
        finally:
            if original_flag:
                os.environ["CLUSTER_ENABLED"] = original_flag
            else:
                os.environ.pop("CLUSTER_ENABLED", None)
    
    def test_single_instance_configuration(self):
        """Test single instance configuration fields"""
        original_id = os.getenv("SINGLE_INSTANCE_ID")
        original_port = os.getenv("SINGLE_INSTANCE_PORT")
        
        try:
            os.environ["SINGLE_INSTANCE_ID"] = "gateway-single-1"
            os.environ["SINGLE_INSTANCE_PORT"] = "9000"
            settings = reload_settings()
            
            assert settings.single_instance_id == "gateway-single-1"
            assert settings.single_instance_port == 9000
        finally:
            if original_id:
                os.environ["SINGLE_INSTANCE_ID"] = original_id
            else:
                os.environ.pop("SINGLE_INSTANCE_ID", None)
            
            if original_port:
                os.environ["SINGLE_INSTANCE_PORT"] = original_port
            else:
                os.environ.pop("SINGLE_INSTANCE_PORT", None)
    
    def test_cluster_configuration_fields(self):
        """Test cluster configuration fields"""
        original_name = os.getenv("CLUSTER_NAME")
        original_node_id = os.getenv("CLUSTER_NODE_ID")
        
        try:
            os.environ["CLUSTER_NAME"] = "test-cluster"
            os.environ["CLUSTER_NODE_ID"] = "node-5"
            os.environ["CLUSTER_NODE_COUNT"] = "5"
            settings = reload_settings()
            
            assert settings.cluster_name == "test-cluster"
            assert settings.cluster_node_id == "node-5"
            assert settings.cluster_node_count == 5
        finally:
            if original_name:
                os.environ["CLUSTER_NAME"] = original_name
            else:
                os.environ.pop("CLUSTER_NAME", None)
            
            if original_node_id:
                os.environ["CLUSTER_NODE_ID"] = original_node_id
            else:
                os.environ.pop("CLUSTER_NODE_ID", None)
            
            os.environ.pop("CLUSTER_NODE_COUNT", None)
    
    def test_redis_cluster_configuration(self):
        """Test Redis cluster configuration"""
        original_enabled = os.getenv("REDIS_CLUSTER_ENABLED")
        original_nodes = os.getenv("REDIS_CLUSTER_NODES")
        
        try:
            os.environ["REDIS_CLUSTER_ENABLED"] = "true"
            os.environ["REDIS_CLUSTER_NODES"] = "node1:6379,node2:6379,node3:6379"
            settings = reload_settings()
            
            assert settings.redis_cluster_enabled is True
            assert len(settings.redis_cluster_nodes_list) == 3
            assert "node1:6379" in settings.redis_cluster_nodes_list
        finally:
            if original_enabled:
                os.environ["REDIS_CLUSTER_ENABLED"] = original_enabled
            else:
                os.environ.pop("REDIS_CLUSTER_ENABLED", None)
            
            if original_nodes:
                os.environ["REDIS_CLUSTER_NODES"] = original_nodes
            else:
                os.environ.pop("REDIS_CLUSTER_NODES", None)
    
    def test_mysql_cluster_configuration(self):
        """Test MySQL cluster configuration"""
        original_enabled = os.getenv("MYSQL_CLUSTER_ENABLED")
        original_nodes = os.getenv("MYSQL_CLUSTER_NODES")
        
        try:
            os.environ["MYSQL_CLUSTER_ENABLED"] = "true"
            os.environ["MYSQL_CLUSTER_NODES"] = "db1:3306,db2:3306,db3:3306"
            os.environ["MYSQL_CLUSTER_READ_REPLICAS"] = "db2:3306,db3:3306"
            os.environ["MYSQL_CLUSTER_WRITE_NODE"] = "db1:3306"
            settings = reload_settings()
            
            assert settings.mysql_cluster_enabled is True
            assert len(settings.mysql_cluster_nodes_list) == 3
            assert len(settings.mysql_read_replicas_list) == 2
            assert settings.mysql_cluster_write_node == "db1:3306"
        finally:
            if original_enabled:
                os.environ["MYSQL_CLUSTER_ENABLED"] = original_enabled
            else:
                os.environ.pop("MYSQL_CLUSTER_ENABLED", None)
            
            if original_nodes:
                os.environ["MYSQL_CLUSTER_NODES"] = original_nodes
            else:
                os.environ.pop("MYSQL_CLUSTER_NODES", None)
            
            os.environ.pop("MYSQL_CLUSTER_READ_REPLICAS", None)
            os.environ.pop("MYSQL_CLUSTER_WRITE_NODE", None)
    
    def test_cluster_coordinator_configuration(self):
        """Test cluster coordinator configuration"""
        original_host = os.getenv("CLUSTER_COORDINATOR_HOST")
        original_port = os.getenv("CLUSTER_COORDINATOR_PORT")
        
        try:
            os.environ["CLUSTER_COORDINATOR_HOST"] = "coordinator.example.com"
            os.environ["CLUSTER_COORDINATOR_PORT"] = "5000"
            settings = reload_settings()
            
            assert settings.cluster_coordinator_host == "coordinator.example.com"
            assert settings.cluster_coordinator_port == 5000
        finally:
            if original_host:
                os.environ["CLUSTER_COORDINATOR_HOST"] = original_host
            else:
                os.environ.pop("CLUSTER_COORDINATOR_HOST", None)
            
            if original_port:
                os.environ["CLUSTER_COORDINATOR_PORT"] = original_port
            else:
                os.environ.pop("CLUSTER_COORDINATOR_PORT", None)
    
    def test_cluster_heartbeat_configuration(self):
        """Test cluster heartbeat configuration"""
        original_interval = os.getenv("CLUSTER_HEARTBEAT_INTERVAL")
        original_timeout = os.getenv("CLUSTER_ELECTION_TIMEOUT")
        
        try:
            os.environ["CLUSTER_HEARTBEAT_INTERVAL"] = "5"
            os.environ["CLUSTER_ELECTION_TIMEOUT"] = "15"
            settings = reload_settings()
            
            assert settings.cluster_heartbeat_interval == 5
            assert settings.cluster_election_timeout == 15
        finally:
            if original_interval:
                os.environ["CLUSTER_HEARTBEAT_INTERVAL"] = original_interval
            else:
                os.environ.pop("CLUSTER_HEARTBEAT_INTERVAL", None)
            
            if original_timeout:
                os.environ["CLUSTER_ELECTION_TIMEOUT"] = original_timeout
            else:
                os.environ.pop("CLUSTER_ELECTION_TIMEOUT", None)
    
    def test_cluster_consensus_algorithm(self):
        """Test cluster consensus algorithm configuration"""
        original_algorithm = os.getenv("CLUSTER_CONSENSUS_ALGORITHM")
        
        try:
            os.environ["CLUSTER_CONSENSUS_ALGORITHM"] = "paxos"
            settings = reload_settings()
            
            assert settings.cluster_consensus_algorithm == "paxos"
        finally:
            if original_algorithm:
                os.environ["CLUSTER_CONSENSUS_ALGORITHM"] = original_algorithm
            else:
                os.environ.pop("CLUSTER_CONSENSUS_ALGORITHM", None)
    
    def test_cluster_leader_election_flag(self):
        """Test cluster leader election flag"""
        original_flag = os.getenv("CLUSTER_ENABLE_LEADER_ELECTION")
        
        try:
            os.environ["CLUSTER_ENABLE_LEADER_ELECTION"] = "false"
            settings = reload_settings()
            
            assert settings.cluster_enable_leader_election is False
        finally:
            if original_flag:
                os.environ["CLUSTER_ENABLE_LEADER_ELECTION"] = original_flag
            else:
                os.environ.pop("CLUSTER_ENABLE_LEADER_ELECTION", None)
    
    def test_redis_cluster_nodes_list_property(self):
        """Test redis_cluster_nodes_list property"""
        original_nodes = os.getenv("REDIS_CLUSTER_NODES")
        
        try:
            os.environ["REDIS_CLUSTER_NODES"] = "  node1:6379  ,  node2:6379  ,  node3:6379  "
            settings = reload_settings()
            
            nodes = settings.redis_cluster_nodes_list
            assert len(nodes) == 3
            assert all(" " not in node for node in nodes)  # No spaces
        finally:
            if original_nodes:
                os.environ["REDIS_CLUSTER_NODES"] = original_nodes
            else:
                os.environ.pop("REDIS_CLUSTER_NODES", None)
    
    def test_mysql_cluster_nodes_list_property(self):
        """Test mysql_cluster_nodes_list property"""
        original_nodes = os.getenv("MYSQL_CLUSTER_NODES")
        
        try:
            os.environ["MYSQL_CLUSTER_NODES"] = "db1:3306,db2:3306"
            settings = reload_settings()
            
            nodes = settings.mysql_cluster_nodes_list
            assert len(nodes) == 2
            assert "db1:3306" in nodes
            assert "db2:3306" in nodes
        finally:
            if original_nodes:
                os.environ["MYSQL_CLUSTER_NODES"] = original_nodes
            else:
                os.environ.pop("MYSQL_CLUSTER_NODES", None)
    
    def test_mysql_read_replicas_list_property(self):
        """Test mysql_read_replicas_list property"""
        original_replicas = os.getenv("MYSQL_CLUSTER_READ_REPLICAS")
        
        try:
            os.environ["MYSQL_CLUSTER_READ_REPLICAS"] = "replica1:3306,replica2:3306,replica3:3306"
            settings = reload_settings()
            
            replicas = settings.mysql_read_replicas_list
            assert len(replicas) == 3
            assert all("replica" in r for r in replicas)
        finally:
            if original_replicas:
                os.environ["MYSQL_CLUSTER_READ_REPLICAS"] = original_replicas
            else:
                os.environ.pop("MYSQL_CLUSTER_READ_REPLICAS", None)
    
    def test_cluster_mode_switching(self):
        """Test switching between single and cluster mode"""
        original_mode = os.getenv("DEPLOYMENT_MODE")
        
        try:
            # Start in single mode
            os.environ["DEPLOYMENT_MODE"] = "single"
            settings1 = reload_settings()
            assert settings1.is_single_instance_mode is True
            
            # Switch to cluster mode
            os.environ["DEPLOYMENT_MODE"] = "cluster"
            settings2 = reload_settings()
            assert settings2.is_cluster_mode is True
            
            # Switch back to single
            os.environ["DEPLOYMENT_MODE"] = "single"
            settings3 = reload_settings()
            assert settings3.is_single_instance_mode is True
        finally:
            if original_mode:
                os.environ["DEPLOYMENT_MODE"] = original_mode
            else:
                os.environ.pop("DEPLOYMENT_MODE", None)

