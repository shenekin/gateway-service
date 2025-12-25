"""
Application settings and configuration management
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application configuration settings"""
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "default")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    
    # SSL/TLS
    ssl_enabled: bool = os.getenv("SSL_ENABLED", "false").lower() == "true"
    ssl_cert_path: str = os.getenv("SSL_CERT_PATH", "/app/certs/cert.pem")
    ssl_key_path: str = os.getenv("SSL_KEY_PATH", "/app/certs/key.pem")
    
    # JWT
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "default-secret-key")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expiration_minutes: int = int(os.getenv("JWT_EXPIRATION_MINUTES", "30"))
    jwt_public_key_path: Optional[str] = os.getenv("JWT_PUBLIC_KEY_PATH")
    jwt_private_key_path: Optional[str] = os.getenv("JWT_PRIVATE_KEY_PATH")
    
    # API Key
    api_key_enabled: bool = os.getenv("API_KEY_ENABLED", "true").lower() == "true"
    api_key_header: str = os.getenv("API_KEY_HEADER", "X-API-Key")
    
    # Database
    mysql_host: str = os.getenv("MYSQL_HOST", "localhost")
    mysql_port: int = int(os.getenv("MYSQL_PORT", "3306"))
    mysql_user: str = os.getenv("MYSQL_USER", "gateway_user")
    mysql_password: str = os.getenv("MYSQL_PASSWORD", "gateway_password")
    mysql_database: str = os.getenv("MYSQL_DATABASE", "gateway_db")
    mysql_pool_size: int = int(os.getenv("MYSQL_POOL_SIZE", "10"))
    mysql_max_overflow: int = int(os.getenv("MYSQL_MAX_OVERFLOW", "20"))
    
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
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_format: str = os.getenv("LOG_FORMAT", "json")
    log_file_path: str = os.getenv("LOG_FILE_PATH", "/app/logs/gateway.log")
    
    # Tracing
    tracing_enabled: bool = os.getenv("TRACING_ENABLED", "true").lower() == "true"
    jaeger_agent_host: str = os.getenv("JAEGER_AGENT_HOST", "localhost")
    jaeger_agent_port: int = int(os.getenv("JAEGER_AGENT_PORT", "6831"))
    service_name: str = os.getenv("SERVICE_NAME", "gateway-service")
    
    # Monitoring
    prometheus_enabled: bool = os.getenv("PROMETHEUS_ENABLED", "true").lower() == "true"
    metrics_port: int = int(os.getenv("METRICS_PORT", "9090"))
    
    # Security
    trusted_proxies: str = os.getenv("TRUSTED_PROXIES", "127.0.0.1,localhost")
    allowed_origins: str = os.getenv("ALLOWED_ORIGINS", "*")
    cors_enabled: bool = os.getenv("CORS_ENABLED", "true").lower() == "true"
    
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
    
    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

