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
- [Dependencies](#dependencies)

## Features

- **Request Routing**: Dynamic route matching and forwarding to backend services
- **Authentication**: JWT and API key authentication support
- **Authorization**: Role-Based Access Control (RBAC)
- **Rate Limiting**: Token bucket algorithm with Redis backend
- **Load Balancing**: Multiple strategies (round-robin, least connections, weighted, random)
- **Circuit Breaker**: Fault tolerance and cascading failure prevention
- **Retry Logic**: Exponential backoff retry mechanism
- **Service Discovery**: Support for Nacos, Consul, and static configuration
- **Distributed Tracing**: OpenTelemetry integration with Jaeger
- **Logging**: Structured JSON logging
- **Health Checks**: Health and readiness endpoints

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
│   │   ├── rbac.py             # Authorization middleware
│   │   ├── rate_limit.py       # Rate limiting middleware
│   │   ├── logging.py          # Logging middleware
│   │   └── tracing.py          # Distributed tracing middleware
│   ├── models/                 # Data models
│   │   ├── route.py            # Route configuration models
│   │   └── context.py          # Request context models
│   ├── adapters/               # External service adapters
│   │   └── huaweicloud.py      # Huawei Cloud adapter
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
│   ├── test_rbac.py
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
- Redis (for rate limiting)
- MySQL 8.0 (for API key storage, optional)
- Nacos/Consul (for service discovery, optional)

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

4. Configure environment variables:
```bash
cp .env.dev .env
# Edit .env with your configuration
```

5. Run the service:
```bash
python -m app.main
# Or using uvicorn directly:
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Configuration

### Environment Variables

Key environment variables (see `.env.dev` for full list):

- `ENVIRONMENT`: Environment name (default, dev, prod)
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `JWT_SECRET_KEY`: JWT secret key
- `JWT_ALGORITHM`: JWT algorithm (HS256 or RS256)
- `REDIS_HOST`: Redis host
- `REDIS_PORT`: Redis port
- `SERVICE_DISCOVERY_TYPE`: Service discovery type (nacos, consul, static)
- `RATE_LIMIT_ENABLED`: Enable rate limiting
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
- **Purpose**: Role-Based Access Control
- **Dependencies**: `app/models/context.py`, `app/models/route.py`
- **Key Functions**:
  - `check_permission()`: Check user permissions
  - `check_role()`: Check user roles
  - `authorize()`: Authorize request

#### Rate Limiting (`app/middleware/rate_limit.py`)
- **Purpose**: Request rate limiting using Redis
- **Dependencies**: `redis`, `app/settings.py`
- **Algorithm**: Token bucket
- **Key Functions**:
  - `check_rate_limit()`: Check if request is within limit
  - `check_request_rate_limit()`: Check rate limit for request

#### Logging (`app/middleware/logging.py`)
- **Purpose**: Structured request/response logging
- **Dependencies**: `app/settings.py`
- **Format**: JSON or text
- **Key Functions**:
  - `_log_request()`: Log request information
  - `_log_response()`: Log response information

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

### Adapter Modules

#### Huawei Cloud Adapter (`app/adapters/huaweicloud.py`)
- **Purpose**: Integration with Huawei Cloud APIs
- **Dependencies**: `httpx`
- **Key Functions**:
  - `authenticate()`: Authenticate with Huawei Cloud
  - `list_ecs_instances()`: List ECS instances
  - `create_ecs_instance()`: Create ECS instance
  - `delete_ecs_instance()`: Delete ECS instance

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
- `tests/test_rbac.py`: RBAC tests
- `tests/test_settings.py`: Settings tests
- `tests/test_models.py`: Model tests

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
│   ├── middleware/rbac.py
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
└── adapters/huaweicloud.py
```

## Code Standards

This project follows the coding standards defined in `Developer_coding_rules_Principles`:
- **L1**: Code style (black/ruff formatting)
- **L2**: Naming conventions (snake_case, PascalCase)
- **L3**: Structure (SRP, function length limits)
- **L4**: Exceptions, logging, security
- **L5**: Architecture principles (SOLID)

## License

[Your License Here]
