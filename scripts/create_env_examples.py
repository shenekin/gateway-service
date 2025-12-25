"""
Script to create example .env files with single and cluster configurations
"""

import os
from pathlib import Path


def create_env_example_file(file_path: Path, env_name: str, deployment_mode: str) -> None:
    """
    Create example environment file with specified configuration
    
    Args:
        file_path: Path to .env file
        env_name: Environment name (default, dev, prod)
        deployment_mode: Deployment mode (single, cluster)
    """
    is_cluster = deployment_mode == "cluster"
    
    content = f"""# Environment: {env_name}
# Deployment Mode: {deployment_mode}
# Generated automatically - modify as needed

ENVIRONMENT={env_name}
DEBUG={'true' if env_name == 'dev' else 'false'}
HOST=0.0.0.0
PORT=8000

# SSL/TLS Configuration
SSL_ENABLED={'true' if env_name == 'prod' else 'false'}
SSL_CERT_PATH=/app/certs/cert.pem
SSL_KEY_PATH=/app/certs/key.pem

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-in-production-{env_name}
JWT_ALGORITHM={'RS256' if env_name == 'prod' else 'HS256'}
JWT_EXPIRATION_MINUTES=30
JWT_PUBLIC_KEY_PATH=/app/certs/public_key.pem
JWT_PRIVATE_KEY_PATH=/app/certs/private_key.pem

# API Key Configuration
API_KEY_ENABLED=true
API_KEY_HEADER=X-API-Key

# Deployment Mode Configuration
DEPLOYMENT_MODE={deployment_mode}
CLUSTER_ENABLED={'true' if is_cluster else 'false'}

# Single Instance Configuration
SINGLE_INSTANCE_ID=gateway-{env_name}-1
SINGLE_INSTANCE_PORT=8000
SINGLE_INSTANCE_HOST=0.0.0.0

# Cluster Configuration
CLUSTER_NAME=gateway-cluster-{env_name}
CLUSTER_NODE_ID=node-1
CLUSTER_NODE_COUNT=3
CLUSTER_COORDINATOR_HOST=localhost
CLUSTER_COORDINATOR_PORT=2379
CLUSTER_HEARTBEAT_INTERVAL=10
CLUSTER_ELECTION_TIMEOUT=30
CLUSTER_REPLICATION_FACTOR=2
CLUSTER_CONSENSUS_ALGORITHM=raft
CLUSTER_SHARED_STORAGE_PATH=/app/shared
CLUSTER_ENABLE_LEADER_ELECTION=true

# MySQL Single Instance Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=gateway_user
MYSQL_PASSWORD=gateway_password_{env_name}
MYSQL_DATABASE=gateway_db_{env_name}
MYSQL_POOL_SIZE={'20' if is_cluster else '10'}
MYSQL_MAX_OVERFLOW={'40' if is_cluster else '20'}

# MySQL Cluster Configuration
MYSQL_CLUSTER_ENABLED={'true' if is_cluster else 'false'}
MYSQL_CLUSTER_NODES=localhost:3306,localhost:3307,localhost:3308
MYSQL_CLUSTER_READ_REPLICAS=localhost:3307,localhost:3308
MYSQL_CLUSTER_WRITE_NODE=localhost:3306
MYSQL_CLUSTER_LOAD_BALANCE_STRATEGY=round_robin
MYSQL_CLUSTER_CONNECTION_TIMEOUT=10
MYSQL_CLUSTER_MAX_RETRIES=3

# Redis Single Instance Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
REDIS_POOL_SIZE={'20' if is_cluster else '10'}

# Redis Cluster Configuration
REDIS_CLUSTER_ENABLED={'true' if is_cluster else 'false'}
REDIS_CLUSTER_NODES=localhost:6379,localhost:6380,localhost:6381
REDIS_CLUSTER_PASSWORD=
REDIS_CLUSTER_SOCKET_TIMEOUT=5
REDIS_CLUSTER_SOCKET_CONNECT_TIMEOUT=5
REDIS_CLUSTER_MAX_CONNECTIONS={'50' if is_cluster else '20'}

# Nacos Single Instance Configuration
NACOS_SERVER_ADDRESSES=localhost:8848
NACOS_NAMESPACE={'prod' if env_name == 'prod' else env_name}
NACOS_GROUP=DEFAULT_GROUP

# Nacos Cluster Configuration
NACOS_CLUSTER_ENABLED={'true' if is_cluster else 'false'}
NACOS_CLUSTER_NODES=localhost:8848,localhost:8849,localhost:8850
NACOS_CLUSTER_NAMESPACE={'prod' if env_name == 'prod' else env_name}
NACOS_CLUSTER_GROUP=DEFAULT_GROUP

# Service Discovery
SERVICE_DISCOVERY_TYPE=nacos
CONSUL_HOST=localhost
CONSUL_PORT=8500
ETCD_HOST=localhost
ETCD_PORT=2379

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE={'200' if env_name == 'dev' else '100'}
RATE_LIMIT_PER_HOUR={'2000' if env_name == 'dev' else '1000'}
RATE_LIMIT_PER_DAY={'20000' if env_name == 'dev' else '10000'}
RATE_LIMIT_STRATEGY=token_bucket

# Circuit Breaker
CIRCUIT_BREAKER_ENABLED=true
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_TIMEOUT_SECONDS=60
CIRCUIT_BREAKER_HALF_OPEN_MAX_CALLS=3

# Retry Configuration
RETRY_ENABLED=true
RETRY_MAX_ATTEMPTS=3
RETRY_BACKOFF_FACTOR=2.0
RETRY_MAX_DELAY_SECONDS=10

# Load Balancer
LOAD_BALANCER_STRATEGY={'least_connections' if is_cluster else 'round_robin'}
LOAD_BALANCER_HEALTH_CHECK_INTERVAL=30

# Logging
LOG_LEVEL={'DEBUG' if env_name == 'dev' else 'INFO'}
LOG_FORMAT=json
LOG_FILE_PATH=/app/logs/gateway-{env_name}.log

# Tracing
TRACING_ENABLED=true
JAEGER_AGENT_HOST=localhost
JAEGER_AGENT_PORT=6831
SERVICE_NAME=gateway-service-{env_name}

# Monitoring
PROMETHEUS_ENABLED=true
METRICS_PORT=9090

# Security
TRUSTED_PROXIES=127.0.0.1,localhost
ALLOWED_ORIGINS=*
CORS_ENABLED=true
"""
    
    file_path.write_text(content)
    print(f"Created {file_path} with {deployment_mode} mode configuration")


def create_all_env_examples(base_path: Optional[Path] = None) -> None:
    """
    Create all example .env files for different environments and deployment modes
    
    Args:
        base_path: Base directory path (default: project root)
    """
    if base_path is None:
        base_path = Path(__file__).parent.parent
    
    env_files = [
        (".env", "default", "single"),
        (".env", "default", "cluster"),
        (".env.dev", "dev", "single"),
        (".env.dev", "dev", "cluster"),
        (".env.prod", "prod", "single"),
        (".env.prod", "prod", "cluster"),
    ]
    
    for filename, env_name, mode in env_files:
        file_path = base_path / filename
        if not file_path.exists():
            create_env_example_file(file_path, env_name, mode)
        else:
            print(f"{file_path} already exists, skipping...")


if __name__ == "__main__":
    import sys
    base_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    create_all_env_examples(base_path)

