"""
Application settings and configuration management
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from functools import lru_cache

# Line 9: Removed top-level import of EnvironmentLoader to fix circular import
# Reason: Circular import occurs when:
#   1. run.py imports get_settings from app.settings
#   2. app.settings imports EnvironmentLoader at module level
#   3. EnvironmentLoader or its dependencies might import get_settings
# Solution: Use lazy import inside functions that need EnvironmentLoader
# This breaks the circular dependency chain


class Settings(BaseSettings):
    """Application configuration settings"""
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "default")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    host: str = os.getenv("HOST", "0.0.0.0")
    # Line 19: Changed default port from 8000 to 8001
    # Reason: Update default port to 8001 as per requirements
    port: int = int(os.getenv("PORT", "8001"))
    
    # SSL/TLS
    ssl_enabled: bool = os.getenv("SSL_ENABLED", "false").lower() == "true"
    ssl_cert_path: str = os.getenv("SSL_CERT_PATH", "/app/certs/cert.pem")
    ssl_key_path: str = os.getenv("SSL_KEY_PATH", "/app/certs/key.pem")
    
    # JWT
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "secret_key")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "RS256")
    jwt_expiration_minutes: int = int(os.getenv("JWT_EXPIRATION_MINUTES", "30"))
    jwt_public_key_path: Optional[str] = os.getenv("JWT_PUBLIC_KEY_PATH")
    jwt_private_key_path: Optional[str] = os.getenv("JWT_PRIVATE_KEY_PATH")
    # Line 41-42: Added refresh token configuration
    # Reason: Support refresh token functionality with configurable expiration
    #         Refresh tokens have longer expiration than access tokens
    jwt_refresh_expiration_days: int = int(os.getenv("JWT_REFRESH_EXPIRATION_DAYS", "7"))
    jwt_refresh_rotation_enabled: bool = os.getenv("JWT_REFRESH_ROTATION_ENABLED", "true").lower() == "true"
    
    # API Key
    api_key_enabled: bool = os.getenv("API_KEY_ENABLED", "true").lower() == "true"
    api_key_header: str = os.getenv("API_KEY_HEADER", "X-API-Key")
    
    # Database
    mysql_host: str = os.getenv("MYSQL_HOST", "localhost")
    mysql_port: int = int(os.getenv("MYSQL_PORT", 3306))
    mysql_user: str = os.getenv("MYSQL_USER", "root")
    mysql_password: str = os.getenv("MYSQL_PASSWORD", "1qaz@WSX")
    mysql_database: str = os.getenv("MYSQL_DATABASE", "gateway_db")
    mysql_pool_size: int = int(os.getenv("MYSQL_POOL_SIZE", 10))
    mysql_max_overflow: int = int(os.getenv("MYSQL_MAX_OVERFLOW", 20))
    
    # Redis
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_password: Optional[str] = os.getenv("REDIS_PASSWORD")
    redis_db: int = int(os.getenv("REDIS_DB", "0"))
    redis_pool_size: int = int(os.getenv("REDIS_POOL_SIZE", "10"))
    
    # Service Discovery
    service_discovery_type: str = os.getenv("SERVICE_DISCOVERY_TYPE", "nacos")
    nacos_server_addresses: str = os.getenv("NACOS_SERVER_ADDRESSES", "localhost:8848")
    nacos_namespace: str = os.getenv("NACOS_NAMESPACE", "public")
    nacos_group: str = os.getenv("NACOS_GROUP", "DEFAULT_GROUP")
    consul_host: str = os.getenv("CONSUL_HOST", "localhost")
    consul_port: int = int(os.getenv("CONSUL_PORT", "8500"))
    etcd_host: str = os.getenv("ETCD_HOST", "localhost")
    etcd_port: int = int(os.getenv("ETCD_PORT", "2379"))
    
    # Rate Limiting
    rate_limit_enabled: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))
    rate_limit_per_hour: int = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))
    rate_limit_per_day: int = int(os.getenv("RATE_LIMIT_PER_DAY", "10000"))
    rate_limit_strategy: str = os.getenv("RATE_LIMIT_STRATEGY", "token_bucket")
    # Line 77-78: Added MySQL integration for rate limiting
    # Reason: Enable MySQL storage for rate limit records alongside Redis
    #         Redis handles fast checking, MySQL provides persistent storage for audit/analytics
    rate_limit_mysql_enabled: bool = os.getenv("RATE_LIMIT_MYSQL_ENABLED", "true").lower() == "true"
    # Line 82: Changed default to False for reliability
    # Reason: Async mode may not complete background tasks before response is sent
    #         Synchronous mode guarantees MySQL writes complete
    #         Users can set RATE_LIMIT_MYSQL_ASYNC=true for faster but less reliable storage
    rate_limit_mysql_async: bool = os.getenv("RATE_LIMIT_MYSQL_ASYNC", "false").lower() == "true"
    
    # Circuit Breaker
    circuit_breaker_enabled: bool = os.getenv("CIRCUIT_BREAKER_ENABLED", "true").lower() == "true"
    circuit_breaker_failure_threshold: int = int(os.getenv("CIRCUIT_BREAKER_FAILURE_THRESHOLD", "5"))
    circuit_breaker_timeout_seconds: int = int(os.getenv("CIRCUIT_BREAKER_TIMEOUT_SECONDS", "60"))
    circuit_breaker_half_open_max_calls: int = int(os.getenv("CIRCUIT_BREAKER_HALF_OPEN_MAX_CALLS", "3"))
    
    # Retry
    retry_enabled: bool = os.getenv("RETRY_ENABLED", "true").lower() == "true"
    retry_max_attempts: int = int(os.getenv("RETRY_MAX_ATTEMPTS", "3"))
    retry_backoff_factor: float = float(os.getenv("RETRY_BACKOFF_FACTOR", "2.0"))
    retry_max_delay_seconds: int = int(os.getenv("RETRY_MAX_DELAY_SECONDS", "10"))
    
    # Load Balancer
    load_balancer_strategy: str = os.getenv("LOAD_BALANCER_STRATEGY", "round_robin")
    load_balancer_health_check_interval: int = int(os.getenv("LOAD_BALANCER_HEALTH_CHECK_INTERVAL", "30"))
    
    # Logging Configuration
    # Line 96-105: Enhanced logging configuration with separate log files for different log types
    # Reason: Different log types (request, error, access, audit) should be saved to separate files
    # This improves log management, filtering, and analysis
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_format: str = os.getenv("LOG_FORMAT", "json")
    # Default log directory: use ./logs for local development, /app/logs for Docker
    _default_log_dir = os.path.join(os.getcwd(), "logs") if os.path.exists(os.getcwd()) else "/app/logs"
    log_file_path: str = os.getenv("LOG_FILE_PATH", os.path.join(_default_log_dir, "gateway.log"))
    log_directory: str = os.getenv("LOG_DIRECTORY", _default_log_dir)
    
    # Separate log file paths for different log types
    log_request_file: str = os.getenv("LOG_REQUEST_FILE", os.path.join(_default_log_dir, "request.log"))
    log_error_file: str = os.getenv("LOG_ERROR_FILE", os.path.join(_default_log_dir, "error.log"))
    log_access_file: str = os.getenv("LOG_ACCESS_FILE", os.path.join(_default_log_dir, "access.log"))
    log_audit_file: str = os.getenv("LOG_AUDIT_FILE", os.path.join(_default_log_dir, "audit.log"))
    log_application_file: str = os.getenv("LOG_APPLICATION_FILE", os.path.join(_default_log_dir, "application.log"))
    
    # Log rotation configuration
    log_max_bytes: int = int(os.getenv("LOG_MAX_BYTES", "10485760"))  # 10MB
    log_backup_count: int = int(os.getenv("LOG_BACKUP_COUNT", "5"))
    
    # Tracing
    tracing_enabled: bool = os.getenv("TRACING_ENABLED", "true").lower() == "true"
    jaeger_agent_host: str = os.getenv("JAEGER_AGENT_HOST", "localhost")
    jaeger_agent_port: int = int(os.getenv("JAEGER_AGENT_PORT", "6831"))
    service_name: str = os.getenv("SERVICE_NAME", "gateway-service")
    
    # Monitoring
    prometheus_enabled: bool = os.getenv("PROMETHEUS_ENABLED", "true").lower() == "true"
    metrics_port: int = int(os.getenv("METRICS_PORT", "9090"))
    
    # Vault Configuration
    # Line 127-140: Added HashiCorp Vault configuration for secret management
    # Reason: Centralized secret management using Vault for JWT keys, API keys, and other sensitive data
    vault_enabled: bool = os.getenv("VAULT_ENABLED", "false").lower() == "true"
    vault_addr: str = os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
    vault_auth_method: str = os.getenv("VAULT_AUTH_METHOD", "approle")  # approle or token
    vault_role_id: Optional[str] = os.getenv("VAULT_ROLE_ID")
    vault_secret_id: Optional[str] = os.getenv("VAULT_SECRET_ID")
    vault_token: Optional[str] = os.getenv("VAULT_TOKEN")
    vault_timeout: int = int(os.getenv("VAULT_TIMEOUT", "5"))  # Connection timeout in seconds
    vault_verify: bool = os.getenv("VAULT_VERIFY", "true").lower() == "true"  # SSL verification for HTTPS
    
    # Vault Secret Paths
    jwt_vault_hs256_path: str = os.getenv("JWT_VAULT_HS256_PATH", "secret/jwt/hs256")
    jwt_vault_rs256_path: str = os.getenv("JWT_VAULT_RS256_PATH", "secret/jwt/rs256")
    api_key_vault_path: str = os.getenv("API_KEY_VAULT_PATH", "secret/api-keys")
    
    # Security
    trusted_proxies: str = os.getenv("TRUSTED_PROXIES", "127.0.0.1,localhost")
    allowed_origins: str = os.getenv("ALLOWED_ORIGINS", "*")
    cors_enabled: bool = os.getenv("CORS_ENABLED", "true").lower() == "true"
    
    # Deployment Mode Configuration (NEW)
    # Line 104-110: Added deployment mode configuration for single instance vs cluster
    deployment_mode: str = os.getenv("DEPLOYMENT_MODE", "single").lower()  # single or cluster
    cluster_enabled: bool = os.getenv("CLUSTER_ENABLED", "false").lower() == "true"
    
    # Single Instance Configuration (NEW)
    # Line 111-115: Added single instance specific settings
    single_instance_id: str = os.getenv("SINGLE_INSTANCE_ID", "gateway-1")
    # Line 114: Changed default single instance port from 8000 to 8001
    # Reason: Update default port to 8001 as per requirements
    single_instance_port: int = int(os.getenv("SINGLE_INSTANCE_PORT", "8001"))
    single_instance_host: str = os.getenv("SINGLE_INSTANCE_HOST", "0.0.0.0")
    
    # Cluster Configuration (NEW)
    # Line 116-130: Added cluster-specific configuration settings
    cluster_name: str = os.getenv("CLUSTER_NAME", "gateway-cluster")
    cluster_node_id: str = os.getenv("CLUSTER_NODE_ID", "node-1")
    cluster_node_count: int = int(os.getenv("CLUSTER_NODE_COUNT", "3"))
    cluster_coordinator_host: str = os.getenv("CLUSTER_COORDINATOR_HOST", "localhost")
    cluster_coordinator_port: int = int(os.getenv("CLUSTER_COORDINATOR_PORT", "2379"))
    cluster_heartbeat_interval: int = int(os.getenv("CLUSTER_HEARTBEAT_INTERVAL", "10"))
    cluster_election_timeout: int = int(os.getenv("CLUSTER_ELECTION_TIMEOUT", "30"))
    cluster_replication_factor: int = int(os.getenv("CLUSTER_REPLICATION_FACTOR", "2"))
    cluster_consensus_algorithm: str = os.getenv("CLUSTER_CONSENSUS_ALGORITHM", "raft")
    cluster_shared_storage_path: str = os.getenv("CLUSTER_SHARED_STORAGE_PATH", "/app/shared")
    cluster_enable_leader_election: bool = os.getenv("CLUSTER_ENABLE_LEADER_ELECTION", "true").lower() == "true"
    
    # Redis Cluster Configuration (NEW)
    # Line 131-137: Added Redis cluster configuration for cluster mode
    redis_cluster_enabled: bool = os.getenv("REDIS_CLUSTER_ENABLED", "false").lower() == "true"
    redis_cluster_nodes: str = os.getenv("REDIS_CLUSTER_NODES", "localhost:6379,localhost:6380,localhost:6381")
    redis_cluster_password: Optional[str] = os.getenv("REDIS_CLUSTER_PASSWORD")
    redis_cluster_socket_timeout: int = int(os.getenv("REDIS_CLUSTER_SOCKET_TIMEOUT", "5"))
    redis_cluster_socket_connect_timeout: int = int(os.getenv("REDIS_CLUSTER_SOCKET_CONNECT_TIMEOUT", "5"))
    redis_cluster_max_connections: int = int(os.getenv("REDIS_CLUSTER_MAX_CONNECTIONS", "50"))
    
    # MySQL Cluster Configuration (NEW)
    # Line 138-145: Added MySQL cluster configuration for cluster mode
    mysql_cluster_enabled: bool = os.getenv("MYSQL_CLUSTER_ENABLED", "false").lower() == "true"
    mysql_cluster_nodes: str = os.getenv("MYSQL_CLUSTER_NODES", "localhost:3306,localhost:3307,localhost:3308")
    mysql_cluster_read_replicas: str = os.getenv("MYSQL_CLUSTER_READ_REPLICAS", "localhost:3306")
    mysql_cluster_write_node: str = os.getenv("MYSQL_CLUSTER_WRITE_NODE", "localhost:3306")
    mysql_cluster_load_balance_strategy: str = os.getenv("MYSQL_CLUSTER_LOAD_BALANCE_STRATEGY", "round_robin")
    mysql_cluster_connection_timeout: int = int(os.getenv("MYSQL_CLUSTER_CONNECTION_TIMEOUT", "10"))
    mysql_cluster_max_retries: int = int(os.getenv("MYSQL_CLUSTER_MAX_RETRIES", "3"))
    
    @property
    def trusted_proxy_list(self) -> List[str]:
        """Get list of trusted proxy IPs"""
        return [ip.strip() for ip in self.trusted_proxies.split(",")]
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Get list of allowed CORS origins"""
        if self.allowed_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    # NEW: Property methods for cluster configuration
    # Line 149-158: Added property methods to get cluster node list and Redis cluster nodes
    @property
    def is_cluster_mode(self) -> bool:
        """
        Check if running in cluster mode
        
        Returns:
            True if cluster mode is enabled
        """
        return self.deployment_mode == "cluster" or self.cluster_enabled
    
    @property
    def is_single_instance_mode(self) -> bool:
        """
        Check if running in single instance mode
        
        Returns:
            True if single instance mode
        """
        return not self.is_cluster_mode
    
    @property
    def redis_cluster_nodes_list(self) -> List[str]:
        """
        Get list of Redis cluster nodes
        
        Returns:
            List of Redis cluster node addresses
        """
        return [node.strip() for node in self.redis_cluster_nodes.split(",")]
    
    @property
    def mysql_cluster_nodes_list(self) -> List[str]:
        """
        Get list of MySQL cluster nodes
        
        Returns:
            List of MySQL cluster node addresses
        """
        return [node.strip() for node in self.mysql_cluster_nodes.split(",")]
    
    @property
    def mysql_read_replicas_list(self) -> List[str]:
        """
        Get list of MySQL read replica addresses
        
        Returns:
            List of read replica addresses
        """
        return [replica.strip() for replica in self.mysql_cluster_read_replicas.split(",")]
    
    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings(env_name: Optional[str] = None, env_file_path: Optional[str] = None) -> Settings:
    """
    Get cached settings instance with optional environment file loading
    
    Args:
        env_name: Environment name (default, dev, prod) - NEW parameter
        env_file_path: Custom path to .env file - NEW parameter
        
    Returns:
        Settings instance
        
    Note:
        Lines 196-203: Added support for loading from external .env files
        This allows switching between .env, .env.dev, .env.prod without code changes
    """
    # Line 204-215: Lazy import of EnvironmentLoader to fix circular import
    # Reason: Importing EnvironmentLoader at module level causes circular import:
    #   - run.py imports get_settings from app.settings
    #   - app.settings imports EnvironmentLoader at top level
    #   - If EnvironmentLoader or dependencies import get_settings, circular import occurs
    # Solution: Import EnvironmentLoader only when needed (lazy import)
    from app.utils.env_loader import EnvironmentLoader
    
    # NEW: Load environment file before creating Settings instance
    # Line 216-222: Environment file loading logic
    if env_file_path:
        EnvironmentLoader.load_environment(base_path=os.path.dirname(env_file_path))
        # Override env_file in Config
        Settings.Config.env_file = os.path.basename(env_file_path)
    elif env_name:
        EnvironmentLoader.load_environment(env_name=env_name)
        # Update env_file based on environment name
        env_file = EnvironmentLoader.get_env_file_path(env_name)
        Settings.Config.env_file = env_file
    
    return Settings()


def reload_settings(env_name: Optional[str] = None, env_file_path: Optional[str] = None) -> Settings:
    """
    Reload settings with new environment configuration
    
    Args:
        env_name: Environment name (default, dev, prod) - NEW function
        env_file_path: Custom path to .env file - NEW function
        
    Returns:
        New Settings instance
        
    Note:
        Lines 227-242: New function to reload settings without cache
        Useful for testing or runtime environment switching
    """
    # Line 228-230: Lazy import of EnvironmentLoader to fix circular import
    # Reason: Same circular import issue as in get_settings()
    # Solution: Import only when needed
    from app.utils.env_loader import EnvironmentLoader
    
    # Clear cache to force reload
    get_settings.cache_clear()
    
    # Load new environment
    if env_file_path:
        EnvironmentLoader.load_environment(base_path=os.path.dirname(env_file_path))
    elif env_name:
        EnvironmentLoader.load_environment(env_name=env_name)
    
    return get_settings(env_name, env_file_path)


def get_available_environments() -> List[str]:
    """
    Get list of available environment configurations
    
    Returns:
        List of available environment names
        
    Note:
        Lines 244-252: New utility function to discover available .env files
    """
    # Line 245-247: Lazy import of EnvironmentLoader to fix circular import
    # Reason: Same circular import issue as in get_settings()
    # Solution: Import only when needed
    from app.utils.env_loader import EnvironmentLoader
    
    return EnvironmentLoader.get_available_environments()

