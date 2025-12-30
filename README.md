# Gateway Service

API Gateway service for Cloud Resource Management System Platform. This service provides routing, authentication, authorization, rate limiting, load balancing, circuit breaking, and request forwarding capabilities.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Modules](#modules)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Deployment](#deployment)
- [External Services Configuration](#external-services-configuration)
- [Dependencies](#dependencies)

## Features

- **Request Routing**: Dynamic route matching and forwarding to backend services
- **Authentication**: JWT and API key authentication support
- **Rate Limiting**: Token bucket algorithm with Redis backend, per-user rate limiting support - *Enhanced: 2025-12-25*
- **Load Balancing**: Multiple strategies (round-robin, least connections, weighted, random)
- **Circuit Breaker**: Fault tolerance and cascading failure prevention
- **Retry Logic**: Exponential backoff retry mechanism
- **Service Discovery**: Support for Nacos, Consul, and static configuration
- **Distributed Tracing**: OpenTelemetry integration with Jaeger
- **Logging**: Structured JSON logging
- **Health Checks**: Health and readiness endpoints
- **Environment Switching**: Support for multiple environment configurations (.env, .env.dev, .env.prod) - *Added: 2024-12-19*
- **Cluster Mode**: Single instance and cluster deployment modes with full cluster configuration - *Added: 2024-12-19*

## Architecture

```
Client → Gateway → [Auth] → [Rate Limit] → [Route Match] → [Load Balance] → Backend Service
                     ↓
              [Circuit Breaker]
                     ↓
              [Retry Handler]
```

## Project Structure

```
gateway-service/
├── run.py                      # Unified entry point - *Added: 2024-12-19*
├── app/
│   ├── __init__.py
│   ├── main.py                 # Main application entry point
│   ├── bootstrap.py            # Application initialization
│   ├── settings.py             # Configuration management
│   ├── core/                   # Core gateway services
│   │   ├── router.py           # Route matching and management
│   │   ├── proxy.py            # HTTP proxy service
│   │   ├── discovery.py        # Service discovery
│   │   ├── load_balancer.py    # Load balancing strategies
│   │   ├── circuit_breaker.py  # Circuit breaker pattern
│   │   └── retry.py            # Retry handler
│   ├── middleware/             # Request middleware
│   │   ├── auth.py             # Authentication middleware
│   │   # rbac.py removed - RBAC not being developed at this stage
│   │   ├── rate_limit.py       # Rate limiting middleware
│   │   ├── logging.py          # Logging middleware
│   │   └── tracing.py          # Distributed tracing middleware
│   ├── models/                 # Data models
│   │   ├── route.py            # Route configuration models
│   │   └── context.py          # Request context models
│   ├── adapters/               # External service adapters
│   │   # huaweicloud.py removed - not being developed at this stage
│   └── utils/                  # Utility modules
│       └── crypto.py           # Cryptographic utilities
├── config/                      # Configuration files
│   ├── routes.yaml             # Route configurations
│   └── services.yaml           # Service instance configurations
├── tests/                       # Unit tests
│   ├── test_router.py
│   ├── test_load_balancer.py
│   ├── test_circuit_breaker.py
│   ├── test_retry.py
│   ├── test_auth.py
│   # test_rbac.py removed - RBAC not being developed at this stage
│   ├── test_settings.py
│   └── test_models.py
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
├── pytest.ini                  # Pytest configuration
└── README.md                   # This file
```

## Installation

### Prerequisites

- Python 3.10+
- **Required Services:**
  - Redis (for rate limiting)
  - MySQL 8.0 (for API key storage and database operations)
- **Optional Services:**
  - Nacos/Consul/etcd (for service discovery, or use static configuration)
  - Jaeger (for distributed tracing)
  - Prometheus (for metrics collection)
- **Backend Services:** Project Service, Auth Service, ECS Service, Dashboard Service (must be running and registered with service discovery)

**See [EXTERNAL_SERVICES_CHECKLIST.md](EXTERNAL_SERVICES_CHECKLIST.md) for complete setup guide.**

### Setup

1. Clone the repository:
```bash
cd gateway-service
```

2. Create virtual environment:
```bash
python3.10 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. **Prepare external services** (see [External Services Configuration](#external-services-configuration)):
```bash
# Verify all external services are ready
python scripts/verify_external_services.py
```

5. Configure environment variables:
```bash
cp .env.dev .env
# Edit .env with your configuration
```

6. Run the service:
```bash
# Recommended: Use unified entry point (run.py)
python run.py

# With development environment
python run.py --env dev --reload

# With production environment
python run.py --env prod

# With custom host and port
python run.py --host 0.0.0.0 --port 9000

# With auto-create environment file
python run.py --env dev --create-env

# With database initialization
python run.py --env dev --init-db

# Legacy: Direct execution (deprecated)
python -m app.main
# Or using uvicorn directly:
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

## External Services Configuration

**Date:** 2025-12-25  
**Purpose:** Complete guide for preparing all external dependencies before starting the gateway service

### Overview

The gateway service requires several external services to function properly. Use the verification script and configuration files to ensure all dependencies are ready.

### Quick Verification

Before starting the gateway, verify all external services:

```bash
python scripts/verify_external_services.py
```

This script checks:
- ✅ Redis connection
- ✅ MySQL connection
- ✅ Database schema initialization
- ✅ Service discovery availability
- ✅ Backend services health
- ✅ Jaeger availability (optional)
- ✅ Log directory writability

### Required Services

#### 1. Redis
- **Purpose:** Rate limiting storage
- **Default:** `localhost:6379`
- **Configuration:** `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`
- **Installation:** `docker run -d --name redis -p 6379:6379 redis:latest`
- **Verification:** `redis-cli ping`

#### 2. MySQL 8.0
- **Purpose:** Database for API keys, routes, service instances
- **Default:** `localhost:3306`
- **Configuration:** `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`
- **Installation:** See `EXTERNAL_SERVICES_CHECKLIST.md`
- **Initialization:** `python scripts/database/init_database.py`

### Optional Services

#### Service Discovery
Choose one:
- **Nacos** (default): `SERVICE_DISCOVERY_TYPE=nacos`
- **Consul**: `SERVICE_DISCOVERY_TYPE=consul`
- **etcd**: `SERVICE_DISCOVERY_TYPE=etcd`
- **Static**: `SERVICE_DISCOVERY_TYPE=static` (uses `config/services.yaml`)

#### Jaeger (Distributed Tracing)
- **Purpose:** Request tracing
- **Default:** `localhost:6831`
- **Configuration:** `TRACING_ENABLED`, `JAEGER_AGENT_HOST`, `JAEGER_AGENT_PORT`
- **UI:** `http://localhost:16686`

#### Prometheus (Monitoring)
- **Purpose:** Metrics collection
- **Configuration:** `PROMETHEUS_ENABLED`, `METRICS_PORT`
- **Endpoint:** `/metrics`

### Configuration Files

- **`config/external_services.yaml`**: Complete configuration reference for all external services
- **`EXTERNAL_SERVICES_CHECKLIST.md`**: Detailed setup guide with installation instructions
- **`scripts/verify_external_services.py`**: Verification script to check all services

### Backend Services

The gateway routes requests to backend services. Ensure these services are running and registered with service discovery:

- **Project Service**: `/projects`, `/projects/{project_id}`
- **Auth Service**: `/auth/login`, `/auth/logout`, `/auth/register`, `/auth/refresh`
- **ECS Service**: `/ecs`, `/ecs/{ecs_id}`
- **Dashboard Service**: `/dashboard`

All backend services must implement `/health` endpoint and be registered with service discovery.

### Cluster Mode

For cluster deployment, additional configuration is required:

- **Redis Cluster**: `REDIS_CLUSTER_ENABLED=true`
- **MySQL Cluster**: `MYSQL_CLUSTER_ENABLED=true`
- **Nacos Cluster**: `NACOS_CLUSTER_ENABLED=true`

See `config/external_services.yaml` for cluster configuration details.

## Configuration

### Environment Variables

Key environment variables (see `.env.dev` for full list):

- `ENVIRONMENT`: Environment name (default, dev, prod)
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8001) - *Updated: 2024-12-19*
- `JWT_SECRET_KEY`: JWT secret key
- `JWT_ALGORITHM`: JWT algorithm (HS256 or RS256)
- `REDIS_HOST`: Redis host
- `REDIS_PORT`: Redis port
- `SERVICE_DISCOVERY_TYPE`: Service discovery type (nacos, consul, static)
- `RATE_LIMIT_ENABLED`: Enable rate limiting
- `RATE_LIMIT_MYSQL_ENABLED`: Enable MySQL storage for rate limit records (default: true) - *Added: 2025-12-25*
- `RATE_LIMIT_MYSQL_ASYNC`: Use asynchronous MySQL storage (default: true) - *Added: 2025-12-25*
- `CIRCUIT_BREAKER_ENABLED`: Enable circuit breaker

### Route Configuration

Routes are configured in `config/routes.yaml`:

```yaml
routes:
  - path: /projects
    service: project-service
    methods: [GET, POST]
    auth_required: true
    rate_limit: 100
    timeout: 30
```

### Service Configuration

Service instances are configured in `config/services.yaml`:

```yaml
services:
  project-service:
    instances:
      - url: http://project-service-1:8000
        weight: 1
        healthy: true
```

### Environment Switching

*Feature added: 2024-12-19*

The gateway service supports loading configuration from multiple environment files:

- `.env` - Default environment
- `.env.dev` - Development environment
- `.env.prod` - Production environment

#### Loading Environment Configuration

```python
from app.settings import get_settings, reload_settings, get_available_environments

# Load default environment
settings = get_settings()

# Load specific environment
settings = get_settings(env_name="dev")  # Loads .env.dev
settings = get_settings(env_name="prod")  # Loads .env.prod

# Load from custom path
settings = get_settings(env_file_path="/path/to/.env.custom")

# Reload settings (clears cache)
settings = reload_settings(env_name="dev")

# Get available environments
environments = get_available_environments()
```

#### Environment File Selection

The environment is selected based on:
1. `env_name` parameter in `get_settings()`
2. `ENVIRONMENT` environment variable
3. Falls back to `.env` if specified file doesn't exist

### Deployment Modes

*Feature added: 2024-12-19*

The gateway service supports two deployment modes:

#### Single Instance Mode (Default)

```bash
DEPLOYMENT_MODE=single
# or
CLUSTER_ENABLED=false
```

Single instance configuration:
- `SINGLE_INSTANCE_ID`: Unique instance identifier
- `SINGLE_INSTANCE_PORT`: Port for single instance
- `SINGLE_INSTANCE_HOST`: Host binding

#### Cluster Mode

```bash
DEPLOYMENT_MODE=cluster
# or
CLUSTER_ENABLED=true
```

Cluster configuration includes:

**Cluster Basics:**
- `CLUSTER_NAME`: Cluster name
- `CLUSTER_NODE_ID`: Current node identifier
- `CLUSTER_NODE_COUNT`: Total number of nodes
- `CLUSTER_COORDINATOR_HOST`: Coordinator host
- `CLUSTER_COORDINATOR_PORT`: Coordinator port

**Cluster Operations:**
- `CLUSTER_HEARTBEAT_INTERVAL`: Heartbeat interval in seconds
- `CLUSTER_ELECTION_TIMEOUT`: Leader election timeout
- `CLUSTER_REPLICATION_FACTOR`: Data replication factor
- `CLUSTER_CONSENSUS_ALGORITHM`: Consensus algorithm (raft, paxos)
- `CLUSTER_SHARED_STORAGE_PATH`: Shared storage path
- `CLUSTER_ENABLE_LEADER_ELECTION`: Enable leader election

**Redis Cluster:**
- `REDIS_CLUSTER_ENABLED`: Enable Redis cluster mode
- `REDIS_CLUSTER_NODES`: Comma-separated list of Redis nodes
- `REDIS_CLUSTER_PASSWORD`: Redis cluster password
- `REDIS_CLUSTER_SOCKET_TIMEOUT`: Socket timeout
- `REDIS_CLUSTER_MAX_CONNECTIONS`: Maximum connections

**MySQL Cluster:**
- `MYSQL_CLUSTER_ENABLED`: Enable MySQL cluster mode
- `MYSQL_CLUSTER_NODES`: Comma-separated list of MySQL nodes
- `MYSQL_CLUSTER_READ_REPLICAS`: Read replica addresses
- `MYSQL_CLUSTER_WRITE_NODE`: Write node address
- `MYSQL_CLUSTER_LOAD_BALANCE_STRATEGY`: Load balance strategy
- `MYSQL_CLUSTER_CONNECTION_TIMEOUT`: Connection timeout
- `MYSQL_CLUSTER_MAX_RETRIES`: Maximum retry attempts

#### Checking Deployment Mode

```python
from app.settings import get_settings

settings = get_settings()

if settings.is_cluster_mode:
    print(f"Running in cluster mode: {settings.cluster_name}")
    print(f"Node ID: {settings.cluster_node_id}")
else:
    print(f"Running in single instance mode: {settings.single_instance_id}")
```

#### Cluster Node Lists

```python
# Get Redis cluster nodes
redis_nodes = settings.redis_cluster_nodes_list
# Returns: ['node1:6379', 'node2:6379', 'node3:6379']

# Get MySQL cluster nodes
mysql_nodes = settings.mysql_cluster_nodes_list
# Returns: ['db1:3306', 'db2:3306', 'db3:3306']

# Get MySQL read replicas
read_replicas = settings.mysql_read_replicas_list
# Returns: ['replica1:3306', 'replica2:3306']
```

## Modules

### Core Modules

#### Router (`app/core/router.py`)
- **Purpose**: Route matching and configuration management
- **Dependencies**: `app/models/route.py`, `app/settings.py`
- **Key Functions**:
  - `find_route(path, method)`: Find matching route
  - `get_all_routes()`: Get all configured routes
  - `reload_routes()`: Reload routes from configuration

#### Proxy Service (`app/core/proxy.py`)
- **Purpose**: HTTP request forwarding to backend services
- **Dependencies**: `app/core/circuit_breaker.py`, `app/core/retry.py`, `httpx`
- **Key Functions**:
  - `forward_request()`: Forward request to backend
  - `forward_streaming_request()`: Forward streaming request

#### Service Discovery (`app/core/discovery.py`)
- **Purpose**: Service instance discovery
- **Dependencies**: `app/settings.py`
- **Supported**: Nacos, Consul, Static configuration
- **Key Functions**:
  - `get_instances(service_name)`: Get service instances
  - `register()`: Register service instance
  - `deregister()`: Deregister service instance

#### Load Balancer (`app/core/load_balancer.py`)
- **Purpose**: Distribute requests across service instances
- **Dependencies**: `app/core/discovery.py`
- **Strategies**: Round-robin, Least connections, Weighted, Random
- **Key Functions**:
  - `select_instance(instances, service_name)`: Select instance

#### Circuit Breaker (`app/core/circuit_breaker.py`)
- **Purpose**: Prevent cascading failures
- **Dependencies**: `app/settings.py`
- **States**: Closed, Open, Half-open
- **Key Functions**:
  - `call()`: Execute with circuit breaker protection
  - `call_async()`: Execute async function with protection

#### Retry Handler (`app/core/retry.py`)
- **Purpose**: Retry failed requests with exponential backoff
- **Dependencies**: `app/settings.py`
- **Key Functions**:
  - `execute()`: Execute with retry logic
  - `execute_async()`: Execute async with retry logic

### Middleware Modules

#### Authentication (`app/middleware/auth.py`)
- **Purpose**: JWT and API key authentication
- **Dependencies**: `python-jose`, `app/settings.py`, `app/utils/crypto.py`
- **Key Functions**:
  - `authenticate_jwt()`: Authenticate using JWT
  - `authenticate_api_key()`: Authenticate using API key
  - `authenticate()`: Try both methods

#### RBAC (`app/middleware/rbac.py`)
- **Status**: Removed - Not being developed at this stage
- **Reason**: RBAC functionality removed as per project requirements
- **Note**: Basic authorization is handled by route configuration (`auth_required` flag)
- **Future**: Fine-grained authorization should be handled by backend services

#### Rate Limiting (`app/middleware/rate_limit.py`)
- **Purpose**: Request rate limiting using Redis
- **Dependencies**: `redis`, `app/settings.py`
- **Algorithm**: Token bucket
- **Key Functions**:
  - `check_rate_limit()`: Check if request is within limit
  - `check_request_rate_limit()`: Check rate limit for request

#### Logging (`app/middleware/logging.py`)
- **Purpose**: Structured request/response logging with separate log files - *Enhanced: 2025-12-25*
- **Dependencies**: `app/settings.py`, `app/utils/log_manager.py`
- **Format**: JSON or text
- **Log Files**: Separate files for different log types:
  - `request.log`: HTTP request/response logs
  - `error.log`: Error and exception logs
  - `access.log`: Access control and authentication logs
  - `audit.log`: Audit trail and security events
  - `application.log`: General application logs
- **Key Functions**:
  - `_log_request()`: Log request information to request.log
  - `_log_response()`: Log response information to appropriate files

#### Tracing (`app/middleware/tracing.py`)
- **Purpose**: Distributed tracing with OpenTelemetry
- **Dependencies**: `opentelemetry`, `app/settings.py`
- **Exporter**: Jaeger
- **Key Functions**:
  - `get_trace_id()`: Get or generate trace ID
  - `get_span_id()`: Get or generate span ID

### Model Modules

#### Route Models (`app/models/route.py`)
- **RouteConfig**: Route configuration model
- **Route**: Route with matching logic
- **Key Methods**:
  - `matches(path, method)`: Check if route matches
  - `extract_path_params(path)`: Extract path parameters

#### Context Models (`app/models/context.py`)
- **UserContext**: User information model
- **RequestContext**: Request tracking model
- **Key Methods**:
  - `to_forward_headers()`: Convert to headers for forwarding

### Utility Modules

#### Crypto Utils (`app/utils/crypto.py`)
- **Purpose**: Cryptographic operations
- **Key Functions**:
  - `hash_api_key()`: Hash API key
  - `verify_api_key()`: Verify API key
  - `generate_rsa_key_pair()`: Generate RSA keys
  - `load_private_key()`: Load private key
  - `load_public_key()`: Load public key

#### Environment Loader (`app/utils/env_loader.py`)
- **Purpose**: Load environment configuration from external .env files - *Added: 2024-12-19*
- **Dependencies**: `python-dotenv`
- **Key Functions**:
  - `get_env_file_path()`: Get path to environment file
  - `load_environment()`: Load environment variables from file
  - `get_available_environments()`: List available environment files
  - `create_example_env_file()`: Create example .env file - *Added: 2024-12-19*
  - `load_environment_with_auto_create()`: Load with automatic file creation - *Added: 2024-12-19*
- **Supported Environments**: default, dev, development, prod, production

#### Log Manager (`app/utils/log_manager.py`)
- **Purpose**: Manage separate log files for different log types - *Added: 2025-12-25*
- **Dependencies**: `logging`, `app/settings.py`
- **Key Functions**:
  - `get_logger()`: Get logger for specific log type
  - `log_request()`: Log to request.log
  - `log_error()`: Log to error.log
  - `log_access()`: Log to access.log
  - `log_audit()`: Log to audit.log
  - `log_application()`: Log to application.log
- **Log Types**: request, error, access, audit, application
- **Features**: Rotating file handlers, separate file per log type

#### Database Initializer (`app/utils/db_init.py`)
- **Purpose**: Database initialization and schema creation - *Added: 2024-12-19*
- **Dependencies**: `asyncmy`
- **Key Functions**:
  - `create_database()`: Create database if it doesn't exist
  - `execute_sql_file()`: Execute SQL file to create tables
  - `initialize()`: Initialize database and tables
  - `check_connection()`: Check database connection

### Adapter Modules

#### Huawei Cloud Adapter (`app/adapters/huaweicloud.py`)
- **Status**: Removed - Not being developed at this stage
- **Reason**: Huawei Cloud adapter functionality removed as per project requirements
- **Note**: Adapter functionality can be re-implemented when needed

## API Endpoints

### Health Check
```
GET /health
```
Returns service health status.

### Readiness Check
```
GET /ready
```
Returns service readiness status (checks dependencies).

### Metrics
```
GET /metrics
```
Returns Prometheus metrics.

### Gateway Routes
All other routes are dynamically configured and forwarded to backend services.

## Testing

Run tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

Test files:
- `tests/test_router.py`: Router tests
- `tests/test_load_balancer.py`: Load balancer tests
- `tests/test_circuit_breaker.py`: Circuit breaker tests
- `tests/test_retry.py`: Retry handler tests
- `tests/test_auth.py`: Authentication tests
- `tests/test_rbac.py`: Removed - RBAC not being developed at this stage
- `tests/test_settings.py`: Settings tests
- `tests/test_models.py`: Model tests
- `tests/test_env_loader.py`: Environment loader tests - *Added: 2024-12-19*
- `tests/test_settings_env_switching.py`: Environment switching tests - *Added: 2024-12-19*
- `tests/test_settings_cluster.py`: Cluster configuration tests - *Added: 2024-12-19*
- `tests/test_run.py`: Unified entry point tests - *Added: 2024-12-19*

## Deployment

### Docker

Build image:
```bash
docker build -t gateway-service:latest .
```

Run container:
```bash
docker run -p 8000:8000 --env-file .env.prod gateway-service:latest
```

### Docker Compose

Example `docker-compose.yml`:
```yaml
version: '3.8'
services:
  gateway:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_HOST=redis
      - MYSQL_HOST=mysql
    depends_on:
      - redis
      - mysql
```

## Dependencies

### Core Dependencies
- `fastapi==0.104.1`: Web framework
- `uvicorn==0.24.0`: ASGI server
- `httpx==0.25.2`: HTTP client
- `pydantic==2.5.0`: Data validation

### Authentication
- `python-jose[cryptography]==3.3.0`: JWT handling
- `cryptography==41.0.7`: Cryptographic operations

### Database & Cache
- `asyncmy==0.2.9`: MySQL async driver
- `redis==5.0.1`: Redis client

### Service Discovery
- `python-consul==1.1.0`: Consul client
- `nacos-sdk-python==1.0.0`: Nacos client

### Monitoring & Tracing
- `opentelemetry-api==1.21.0`: OpenTelemetry API
- `opentelemetry-sdk==1.21.0`: OpenTelemetry SDK
- `prometheus-client==0.19.0`: Prometheus metrics

### Testing
- `pytest==7.4.3`: Testing framework
- `pytest-asyncio==0.21.1`: Async test support
- `pytest-cov==4.1.0`: Coverage reporting

## Module Dependencies Summary

```
main.py
├── bootstrap.py
│   ├── settings.py
│   ├── middleware/auth.py
│   │   ├── settings.py
│   │   └── utils/crypto.py
│   # middleware/rbac.py removed - RBAC not being developed at this stage
│   │   ├── models/context.py
│   │   └── models/route.py
│   ├── middleware/rate_limit.py
│   │   └── settings.py
│   ├── middleware/logging.py
│   │   └── settings.py
│   ├── middleware/tracing.py
│   │   └── settings.py
│   ├── core/router.py
│   │   ├── models/route.py
│   │   └── settings.py
│   ├── core/discovery.py
│   │   └── settings.py
│   └── core/proxy.py
│       ├── core/circuit_breaker.py
│       │   └── settings.py
│       ├── core/retry.py
│       │   └── settings.py
│       └── settings.py
└── adapters/  # huaweicloud.py removed - not being developed at this stage
```

## Code Standards

This project follows the coding standards defined in `Developer_coding_rules_Principles`:
- **L1**: Code style (black/ruff formatting)
- **L2**: Naming conventions (snake_case, PascalCase)
- **L3**: Structure (SRP, function length limits)
- **L4**: Exceptions, logging, security
- **L5**: Architecture principles (SOLID)

## Database Initialization

*Feature added: 2024-12-19*

The gateway service includes database initialization scripts for automatic and manual database setup.

### Automatic Database Initialization

The database can be initialized automatically using the Python script:

```bash
# Initialize database for default environment
python scripts/database/init_database.py

# Initialize database for specific environment
python scripts/database/init_database.py --env dev
python scripts/database/init_database.py --env prod

# Initialize with custom SQL file
python scripts/database/init_database.py --sql-file /path/to/custom.sql

# Check database connection only
python scripts/database/init_database.py --check-only
```

### Manual Database Initialization

You can also initialize the database manually using the SQL script:

```bash
# Using MySQL command line
mysql -u root -p < scripts/database/init_database.sql

# Or specify database
mysql -u root -p gateway_db < scripts/database/init_database.sql
```

### Database Schema

The initialization script creates the following tables:

- **api_keys**: Stores API keys for authentication
- **routes**: Stores route configurations
- **service_instances**: Stores service instance information
- **rate_limit_records**: Stores rate limiting records
- **circuit_breaker_states**: Stores circuit breaker states
- **audit_logs**: Stores audit logs for gateway operations

### Using Database Initializer in Code

```python
from app.utils.db_init import DatabaseInitializer
import asyncio

# Initialize database
result = asyncio.run(DatabaseInitializer.initialize(env_name="dev"))

# Check connection
is_connected = asyncio.run(DatabaseInitializer.check_connection(env_name="dev"))
```

## Automatic Environment File Creation

*Feature added: 2024-12-19*

The gateway service can automatically create example `.env` files when they don't exist.

### Creating Example Environment Files

```bash
# Create all example .env files
python scripts/create_env_examples.py

# Create in specific directory
python scripts/create_env_examples.py /path/to/directory
```

### Auto-Creation on Load

When loading an environment file that doesn't exist, the system can automatically create an example file:

```python
from app.utils.env_loader import EnvironmentLoader

# Load environment with auto-creation
EnvironmentLoader.load_environment_with_auto_create(
    env_name="dev",
    deployment_mode="single"  # or "cluster"
)
```

### Environment File Structure

Each `.env` file includes:
- Basic server configuration
- Single instance configuration
- Cluster configuration (when cluster mode enabled)
- MySQL single and cluster configurations
- Redis single and cluster configurations
- Nacos single and cluster configurations
- All other gateway service settings

## Running the Service

*Feature added: 2024-12-19*

The gateway service provides a unified entry point (`run.py`) for starting the service with various configuration options.

### Basic Usage

```bash
# Start with default settings
python run.py

# Start with development environment
python run.py --env dev

# Start with production environment
python run.py --env prod
```

### Command Line Options

```bash
python run.py [OPTIONS]

Options:
  --env {default,dev,prod}     Environment name
  --host HOST                  Host to bind to (default: from settings)
  --port PORT                  Port to bind to (default: 8001)
  --reload                     Enable auto-reload (development)
  --workers N                  Number of worker processes
  --deployment-mode {single,cluster}  Deployment mode
  --log-level {debug,info,warning,error,critical}  Log level
  --create-env                 Create example .env file if missing
  --init-db                    Initialize database before starting
```

### Examples

```bash
# Development with auto-reload
python run.py --env dev --reload

# Production with multiple workers
python run.py --env prod --workers 4

# Custom host and port
python run.py --host 127.0.0.1 --port 9000

# With environment file auto-creation
python run.py --env dev --create-env

# With database initialization
python run.py --env dev --init-db

# Cluster mode
python run.py --env prod --deployment-mode cluster
```

### Port Configuration

The default port has been updated to **8001** (previously 8000). This can be configured via:
- Environment variable: `PORT=8001`
- Command line: `python run.py --port 8001`
- Settings file: Update `.env` file with `PORT=8001`

## Logging Configuration

*Feature enhanced: 2025-12-25*

The gateway service now supports separate log files for different log types, improving log management and analysis.

### Log File Types

The service creates separate log files for different purposes:

- **`request.log`**: HTTP request and response logs
- **`error.log`**: Error and exception logs
- **`access.log`**: Access control and authentication logs
- **`audit.log`**: Audit trail and security events
- **`application.log`**: General application logs

### Configuration

Environment variables for logging:

```bash
# Log directory
LOG_DIRECTORY=/app/logs

# Individual log file paths
LOG_REQUEST_FILE=/app/logs/request.log
LOG_ERROR_FILE=/app/logs/error.log
LOG_ACCESS_FILE=/app/logs/access.log
LOG_AUDIT_FILE=/app/logs/audit.log
LOG_APPLICATION_FILE=/app/logs/application.log

# Log rotation
LOG_MAX_BYTES=10485760  # 10MB
LOG_BACKUP_COUNT=5

# Log format and level
LOG_LEVEL=INFO
LOG_FORMAT=json  # or text
```

### Using Log Manager

```python
from app.utils.log_manager import LogManager

log_manager = LogManager()

# Log request
log_manager.log_request("Request received", {"request_id": "123"})

# Log error
log_manager.log_error("Error occurred", {"error_code": "500"}, exc_info=True)

# Log access
log_manager.log_access("User authenticated", {"user_id": "123"})

# Log audit
log_manager.log_audit("Security event", {"action": "login"})

# Log application
log_manager.log_application("Application started", "INFO")
```

### Log File Structure

```
/app/logs/
├── request.log          # HTTP requests/responses
├── request.log.1        # Rotated request logs
├── error.log            # Errors and exceptions
├── error.log.1          # Rotated error logs
├── access.log           # Access control logs
├── audit.log            # Audit trail logs
└── application.log      # Application logs
```

## Changelog

### 2025-12-30 - Production-Ready JWT Authentication

**Feature Added:**
- Production-grade JWT authentication with access_token validation
- Refresh token management with rotation support
- Audit logging for authentication events
- Enhanced header forwarding to backend services

**Purpose:**
- Gateway validates client access_token, all backend services trust gateway
- Support refresh token rotation for enhanced security
- Track authentication events (login, refresh, revoke) for audit and compliance
- Forward user context (user_id, roles, permissions) to backend services

**Root Cause Analysis:**
- Previous implementation had basic JWT validation but lacked production features
- No refresh token management or rotation
- No audit logging for authentication events
- Backend services needed user context in headers

**Solution:**
- Enhanced JWT authentication to extract roles/permissions from access_token
- Created TokenManager for refresh token storage in Redis with rotation
- Created AuditLogger for logging authentication events to MySQL
- Added /auth/refresh and /auth/revoke endpoints
- Enhanced header forwarding to include user_id, roles, and permissions

**Files Created:**
- `app/utils/token_manager.py`: Refresh token management with Redis storage (lines 1-175)
- `app/utils/audit_logger.py`: Audit logging for authentication events (lines 1-145)
- `app/routers/auth.py`: Authentication endpoints (/auth/refresh, /auth/revoke) (lines 1-200)
- `tests/test_token_manager.py`: Unit tests for TokenManager (10+ test methods)
- `tests/test_audit_logger.py`: Unit tests for AuditLogger (5+ test methods)
- `tests/test_auth_router.py`: Unit tests for auth router (6+ test methods)
- `scripts/database/update_audit_logs.sql`: Database migration for audit_logs table

**Files Modified:**
- `app/middleware/auth.py`:
  - Line 90-106: Enhanced JWT payload extraction with roles/permissions parsing
  - Reason: Ensure roles and permissions are extracted from access_token
- `app/models/context.py`:
  - Line 70-82: Enhanced header forwarding with permissions
  - Reason: Forward user_id, roles, and permissions to backend services
- `app/main.py`:
  - Line 19-20: Added auth router inclusion
  - Line 169-183: Enhanced authentication comments
  - Reason: Add /auth/refresh and /auth/revoke endpoints
- `app/settings.py`:
  - Line 41-42: Added refresh token configuration
  - Reason: Support refresh token expiration and rotation settings
- `app/utils/__init__.py`:
  - Line 9-10: Added TokenManager and AuditLogger exports

**Features:**
- **Access Token Validation**: Gateway validates client access_token
- **Backend Trust**: All backend services trust gateway, receive user context in headers
- **Refresh Token Management**: Refresh tokens stored in Redis with expiration
- **Token Rotation**: Old refresh token invalidated when new one is issued (configurable)
- **Roles/Permissions**: Extracted from access_token and forwarded to backend services
- **Header Forwarding**: X-User-Id, X-Roles, X-Permissions forwarded to backend services
- **Audit Logging**: Login, refresh, and revoke events logged to MySQL

**Configuration:**
```bash
# JWT Configuration
JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=RS256
JWT_EXPIRATION_MINUTES=30
JWT_REFRESH_EXPIRATION_DAYS=7
JWT_REFRESH_ROTATION_ENABLED=true
```

**API Endpoints:**
- `POST /auth/refresh`: Refresh access token using refresh token
- `POST /auth/revoke`: Revoke refresh token

**Database Migration:**
Run the migration script to update audit_logs table:
```bash
mysql -u root -p gateway_db < scripts/database/update_audit_logs.sql
```

**Testing:**
- Unit tests cover token management, audit logging, and auth endpoints
- All tests verify error handling and edge cases
- Mock Redis and MySQL for isolated testing

**Backward Compatibility:**
- All existing functionality preserved
- Existing JWT authentication continues to work
- New features are additive, no breaking changes

### 2025-12-25 - MySQL Rate Limit Storage Fix

**Issue Fixed:** MySQL `rate_limit_records` table was empty, records only appeared in Redis.

**Root Cause:**
- Background tasks created with `asyncio.create_task()` were not being tracked, potentially leading to garbage collection before completion
- Errors in background tasks were being silently ignored
- Missing error logging made it impossible to diagnose failures
- MySQL deprecation warning for `VALUES()` function

**Solution:**
- Added background task tracking to prevent garbage collection
- Enhanced error handling and logging for MySQL storage operations
- Added diagnostic script (`scripts/test_mysql_rate_limit_storage.py`) to test MySQL storage independently
- **Fixed MySQL deprecation warning**: Updated SQL to use alias syntax (`AS new`) instead of deprecated `VALUES()` function

**Files Modified:**
- `app/middleware/rate_limit.py`: Added `asyncio` import, background task tracking, enhanced error handling
- `app/utils/rate_limit_storage.py`: Added comprehensive error logging, fixed SQL deprecation warning

**Files Created:**
- `scripts/test_mysql_rate_limit_storage.py`: Diagnostic script for MySQL storage testing
- `MYSQL_STORAGE_FIX.md`: Detailed documentation of the fix

**Testing:**
```bash
# Test MySQL storage independently
python scripts/test_mysql_rate_limit_storage.py
```

**Configuration:**
- Ensure `RATE_LIMIT_MYSQL_ENABLED=true` in `.env` file
- Set `RATE_LIMIT_MYSQL_ASYNC=true` for async storage (faster but may not complete) or `false` for synchronous storage (slower but guaranteed)

**Important:** If records appear in Redis but not in MySQL, set `RATE_LIMIT_MYSQL_ASYNC=false` to use synchronous storage. Background tasks in async mode may not complete before the response is sent.

**See:** 
- [MYSQL_STORAGE_FIX.md](MYSQL_STORAGE_FIX.md) for complete details
- [MYSQL_STORAGE_TROUBLESHOOTING.md](MYSQL_STORAGE_TROUBLESHOOTING.md) for troubleshooting guide

---

### 2025-12-25 - MySQL Integration with Redis Rate Limiting

**Feature Added:**
- Integrated MySQL storage with Redis rate limiting
- Added persistent storage for rate limit records alongside Redis fast checking

**Purpose:**
- Store rate limit records in MySQL for audit and analytics
- Maintain Redis for fast in-memory rate limit checking
- Provide historical data and statistics for rate limit usage

**Root Cause Analysis:**
- Current implementation uses Redis only for rate limiting
- No persistent storage for rate limit records
- Cannot track historical rate limit usage or perform analytics
- Missing audit trail for rate limit events

**Solution:**
- Created `RateLimitStorage` utility class for MySQL operations
- Integrated MySQL storage with existing Redis rate limiting
- Store rate limit records asynchronously to avoid blocking
- Added configuration options to enable/disable MySQL storage

**Files Created:**
- `app/utils/rate_limit_storage.py`: MySQL storage utility for rate limit records (lines 1-295)
- `tests/test_rate_limit_mysql_integration.py`: Unit tests for MySQL integration (10+ test methods)

**Files Modified:**
- `app/middleware/rate_limit.py`:
  - Line 11: Added `RateLimitStorage` import
  - Line 25-26: Added MySQL storage initialization
  - Line 72-137: Enhanced `check_rate_limit()` to store records in MySQL
  - Line 139-200: Added `_store_rate_limit_record_async()` method
- `app/settings.py`:
  - Line 77-78: Added `rate_limit_mysql_enabled` and `rate_limit_mysql_async` configuration
- `app/utils/__init__.py`:
  - Added `RateLimitStorage` to exports

**Features:**
- **Dual Storage**: Redis for fast checking, MySQL for persistence
- **Asynchronous Storage**: MySQL writes don't block rate limit checks
- **Audit Trail**: All rate limit events stored in MySQL
- **Analytics**: Query rate limit history and statistics
- **Backward Compatible**: Works with Redis-only mode if MySQL is disabled

**Database Table:**
- `rate_limit_records`: Stores rate limit records with identifier, window type, request count, timestamps
- See `scripts/database/init_database.sql` for schema

**Configuration:**
```bash
RATE_LIMIT_MYSQL_ENABLED=true   # Enable MySQL storage (default: true)
RATE_LIMIT_MYSQL_ASYNC=true     # Use async storage (default: true)
```

**Usage:**
- MySQL storage is enabled by default
- Rate limit records are automatically stored in MySQL
- Use `RateLimitStorage` class to query history and statistics
- Can be disabled with `RATE_LIMIT_MYSQL_ENABLED=false`

**Verification:**
- Unit tests verify MySQL integration works correctly
- Rate limiting continues to work even if MySQL is unavailable
- Records are stored asynchronously to avoid blocking

### 2025-12-25 - External Services Configuration

**Feature Added:**
- Added comprehensive external services configuration and verification system
- Created configuration files and documentation for all external dependencies

**Purpose:**
- Help users prepare all external services before starting the gateway
- Provide clear checklist of required and optional services
- Enable automated verification of service availability

**Root Cause Analysis:**
- Gateway service depends on multiple external services (Redis, MySQL, Service Discovery, etc.)
- Users need clear guidance on what services to prepare
- Manual verification of services is error-prone and time-consuming
- No centralized documentation for all external dependencies

**Solution:**
- Created `config/external_services.yaml`: Complete configuration reference for all external services
- Created `EXTERNAL_SERVICES_CHECKLIST.md`: Detailed setup guide with installation instructions
- Created `scripts/verify_external_services.py`: Automated verification script
- Added comprehensive unit tests for verification script
- Updated README.md with external services configuration section

**Files Created:**
- `config/external_services.yaml`: External services configuration reference
- `EXTERNAL_SERVICES_CHECKLIST.md`: Complete setup guide with installation instructions
- `scripts/verify_external_services.py`: Service verification script
- `tests/test_external_services_verification.py`: Unit tests for verification script

**Files Modified:**
- `README.md`: Updated Prerequisites section, added External Services Configuration section, updated changelog

**Features:**
- **Service Verification Script**: Checks Redis, MySQL, database schema, service discovery, Jaeger, backend services, and log directory
- **Configuration Reference**: Complete YAML file with all service configurations, installation commands, and health checks
- **Detailed Checklist**: Markdown document with step-by-step setup instructions
- **Comprehensive Tests**: 20+ test methods covering all verification scenarios

**Verification:**
- Verification script successfully checks all required services
- Configuration files provide complete reference for all services
- Unit tests cover all verification scenarios
- Documentation is comprehensive and easy to follow

**Usage:**
```bash
# Verify all external services before starting gateway


# Check configuration reference
cat config/external_services.yaml

# Follow setup guide
cat EXTERNAL_SERVICES_CHECKLIST.md
```

### 2025-12-25 - Huawei Cloud Adapter Removal and Separate Log Files

**Changes:**
- Removed Huawei Cloud adapter functionality (not being developed)
- Implemented separate log files for different log types
- Enhanced logging middleware with LogManager

**Huawei Cloud Adapter Removal:**
- Removed `app/adapters/huaweicloud.py` file
- Updated `app/adapters/__init__.py` to remove HuaweiCloudAdapter export

**Separate Log Files Implementation:**
- Created `app/utils/log_manager.py` for managing separate log files
- Enhanced `app/middleware/logging.py` to use LogManager
- Added logging configuration to `app/settings.py`:
  - Separate log file paths (request, error, access, audit, application)
  - Log rotation configuration
  - Log directory configuration

**Log File Types:**
- `request.log`: HTTP request/response logs
- `error.log`: Error and exception logs
- `access.log`: Access control and authentication logs
- `audit.log`: Audit trail and security events
- `application.log`: General application logs

**Files Modified:**
- `app/adapters/__init__.py`: Removed HuaweiCloudAdapter (line 5)
- `app/settings.py`: Added separate log file configuration (lines 96-105)
- `app/middleware/logging.py`: Enhanced to use LogManager (lines 19-110)
- `app/utils/__init__.py`: Added LogManager export

**New Files:**
- `app/utils/log_manager.py`: Log manager for separate log files
- `tests/test_log_manager.py`: Log manager tests
- `tests/test_logging_middleware_separate_files.py`: Logging middleware tests
- `tests/test_huaweicloud_removal.py`: Huawei Cloud removal verification tests

**New Tests:**
- `tests/test_log_manager.py`: 10 test methods for log manager
- `tests/test_logging_middleware_separate_files.py`: 5 test methods for logging middleware
- `tests/test_huaweicloud_removal.py`: 4 test methods for Huawei Cloud removal

**Impact:**
- No breaking changes to existing functionality
- Logging now uses separate files for better organization
- Log rotation prevents log files from growing too large
- All existing logging functionality preserved

### 2025-12-25 - RBAC Functionality Removal

**Change:**
- Removed RBAC (Role-Based Access Control) functionality from gateway service

**Reason:**
- RBAC is not being developed at this stage as per project requirements
- Removed to simplify the codebase and focus on core gateway functionality

**Files Removed:**
- `app/middleware/rbac.py`: RBAC middleware implementation
- `tests/test_rbac.py`: RBAC unit tests

**Files Modified:**
- `app/bootstrap.py`: 
  - Line 9: Removed RBACMiddleware import
  - Line 48: Removed RBACMiddleware from middleware stack
- `app/main.py`:
  - Line 12: Removed RBACMiddleware import
  - Line 20: Removed RBACMiddleware initialization
  - Line 177: Removed RBAC authorization call
- `app/middleware/__init__.py`:
  - Line 6: Removed RBACMiddleware import
  - Removed from __all__ export

**Authorization Approach:**
- Basic authorization is handled by route configuration (`auth_required` flag)
- Authentication is still performed via JWT and API keys
- Fine-grained authorization should be handled by backend services

**Impact:**
- No breaking changes to existing functionality
- Authentication still works correctly
- Route-level authorization via `auth_required` flag still works
- All other middleware and functionality preserved

### 2025-12-25 - JWT Import Fix

**Bug Fixed:**
- Fixed JWT import error: `ModuleNotFoundError: No module named 'jwt'`

**Root Cause:**
- Code in `app/middleware/auth.py` uses PyJWT API (`jwt.decode()`, `jwt.ExpiredSignatureError`, `jwt.InvalidTokenError`)
- `requirements.txt` only had `python-jose` which has a different API
- PyJWT package was missing from dependencies
- When importing `jwt` module, Python couldn't find it because PyJWT wasn't installed

**Solution:**
- Added `PyJWT==2.8.0` to `requirements.txt`
- Added explanatory comments in `app/middleware/auth.py` (lines 5-15)
- Import statement `import jwt` is correct for PyJWT package

**Files Modified:**
- `requirements.txt`: Added PyJWT==2.8.0 (line 13)
- `app/middleware/auth.py`: Added root cause analysis comments (lines 5-15)

**New Tests:**
- `tests/test_jwt_import_fix.py`: 11 test methods covering:
  - JWT module import
  - JWT function availability
  - JWT exception classes
  - Auth middleware import and initialization
  - JWT decode functionality
  - Token expiration handling
  - Invalid token handling
  - Authentication flow

**Verification:**
- JWT module can be imported successfully
- Auth middleware can be initialized
- JWT authentication works correctly
- All existing functionality preserved

### 2025-12-25 - Circular Import Fix

**Bug Fixed:**
- Fixed circular import error: `ImportError: cannot import name 'get_settings' from partially initialized module 'app.settings'`

**Root Cause:**
- `app/settings.py` imported `EnvironmentLoader` at module level (line 9)
- When `run.py` imported `get_settings` from `app.settings`, Python started loading the module
- The top-level import of `EnvironmentLoader` created a circular dependency chain
- This caused the "partially initialized module" error

**Solution:**
- Changed `EnvironmentLoader` import from top-level to lazy import (inside functions)
- Lazy imports break the circular dependency by deferring import until function execution
- Applied fix to `get_settings()`, `reload_settings()`, and `get_available_environments()` functions

**Files Modified:**
- `app/settings.py`: 
  - Line 9: Removed top-level `EnvironmentLoader` import
  - Lines 204-215: Added lazy import in `get_settings()`
  - Lines 228-230: Added lazy import in `reload_settings()`
  - Lines 245-247: Added lazy import in `get_available_environments()`

**New Tests:**
- `tests/test_circular_import_fix.py`: 10 test methods covering circular import scenarios

**Verification:**
- All imports now work without circular import errors
- Project can start successfully using `python run.py`
- All existing functionality preserved

### 2024-12-19 - Unified Entry Point and Port Update

**New Features:**
- Added unified entry point `run.py` for starting the gateway service
- Updated default port from 8000 to 8001
- Added command-line argument parsing for flexible configuration
- Added support for environment file auto-creation on startup
- Added support for database initialization on startup
- Added deployment mode selection via command line
- Added worker process configuration
- Added log level configuration via command line

**New Files:**
- `run.py`: Unified entry point script - *Added: 2024-12-19*

**Modified Files:**
- `app/settings.py`: Updated default port to 8001 (line 19) - *Updated: 2024-12-19*
- `app/settings.py`: Updated single instance port to 8001 (line 114) - *Updated: 2024-12-19*
- `scripts/create_env_examples.py`: Updated default port to 8001 - *Updated: 2024-12-19*
- `Dockerfile`: Updated port to 8001 and changed CMD to use run.py - *Updated: 2024-12-19*
- `app/main.py`: Added deprecation warning for direct execution - *Updated: 2024-12-19*
- `tests/test_settings.py`: Updated port assertion to 8001 - *Updated: 2024-12-19*

**New Tests:**
- `tests/test_run.py`: Comprehensive tests for run.py entry point - *Added: 2024-12-19*

**Port Changes:**
- Default port changed from 8000 to 8001 across all configuration files
- All gateway service port references updated to 8001
- Backend service ports remain unchanged (still 8000)

### 2024-12-19 - Database Initialization and Auto Environment Creation

**New Features:**
- Added automatic database initialization scripts (SQL and Python)
- Added database schema creation for all gateway tables
- Added automatic .env file creation when files don't exist
- Added example .env file generation script
- Added support for single and cluster configurations in example files
- Added database connection checking utility
- Added manual and automatic database initialization options

**Database Tables Created:**
- `api_keys`: API key storage and management
- `routes`: Route configuration storage
- `service_instances`: Service instance tracking
- `rate_limit_records`: Rate limiting records
- `circuit_breaker_states`: Circuit breaker state tracking
- `audit_logs`: Gateway operation audit logs

**New Features:**
- Added support for loading configuration from external `.env` files
- Added environment switching between `.env`, `.env.dev`, and `.env.prod`
- Added single instance deployment mode configuration
- Added cluster deployment mode with full cluster configuration
- Added Redis cluster configuration support
- Added MySQL cluster configuration support
- Added cluster coordinator and consensus algorithm configuration
- Added utility functions for environment discovery and reloading

**New Modules:**
- `app/utils/env_loader.py`: Environment file loader utility
- `app/utils/db_init.py`: Database initialization utility - *Added: 2024-12-19*
- Enhanced `app/settings.py` with cluster configuration fields

**New Scripts:**
- `scripts/create_env_examples.py`: Script to create example .env files - *Added: 2024-12-19*
- `scripts/database/init_database.py`: Python database initialization script - *Added: 2024-12-19*
- `scripts/database/init_database.sql`: SQL database initialization script - *Added: 2024-12-19*
- `scripts/verify_external_services.py`: External services verification script - *Added: 2025-12-25*

**New Configuration Files:**
- `config/external_services.yaml`: Complete external services configuration reference - *Added: 2025-12-25*
- `EXTERNAL_SERVICES_CHECKLIST.md`: Detailed external services setup guide - *Added: 2025-12-25*
- `docs/DATABASE_SCHEMA_RATE_LIMITING.md`: Database schema documentation for rate limiting - *Added: 2025-12-25*
- `app/utils/rate_limit_storage.py`: MySQL storage utility for rate limit records - *Added: 2025-12-25*

**New Tests:**
- `tests/test_env_loader.py`: Environment loader unit tests
- `tests/test_settings_env_switching.py`: Environment switching tests
- `tests/test_settings_cluster.py`: Cluster configuration tests
- `tests/test_env_auto_create.py`: Environment auto-creation tests - *Added: 2024-12-19*
- `tests/test_database_init.py`: Database initialization tests - *Added: 2024-12-19*
- `tests/test_circular_import_fix.py`: Circular import fix tests - *Added: 2025-12-25*
- `tests/test_jwt_import_fix.py`: JWT import fix tests - *Added: 2025-12-25*
- `tests/test_rbac_removal.py`: RBAC removal verification tests - *Added: 2025-12-25*
- `tests/test_log_manager.py`: Log manager tests - *Added: 2025-12-25*
- `tests/test_logging_middleware_separate_files.py`: Logging middleware separate files tests - *Added: 2025-12-25*
- `tests/test_huaweicloud_removal.py`: Huawei Cloud removal verification tests - *Added: 2025-12-25*
- `tests/test_external_services_verification.py`: External services verification tests - *Added: 2025-12-25*
- `tests/test_rate_limit_per_user.py`: Per-user rate limiting tests - *Added: 2025-12-25*
- `tests/test_rate_limit_mysql_integration.py`: MySQL integration tests - *Added: 2025-12-25*

**Modified Files:**
- `app/settings.py`: Added cluster configuration fields (lines 104-158)
- `app/settings.py`: Enhanced `get_settings()` with environment switching (lines 196-225)
- `app/utils/env_loader.py`: Added auto-creation methods (lines 108-175) - *Added: 2024-12-19*
- `app/utils/__init__.py`: Added EnvironmentLoader and DatabaseInitializer exports

**Backward Compatibility:**
- All existing functionality remains unchanged
- Default behavior unchanged (single instance mode)
- Existing environment variable loading still works

## License

[Your License Here]
