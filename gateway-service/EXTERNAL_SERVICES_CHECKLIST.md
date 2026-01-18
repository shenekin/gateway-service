# External Services Configuration Checklist

**Date:** 2025-12-25  
**Purpose:** Complete checklist of all external services and dependencies required for gateway-service

## Overview

This document lists all external services, dependencies, and configurations needed before starting the gateway service. Use this checklist to prepare your environment.

## Required Services (Must Have)

### 1. Redis

**Purpose:** Rate limiting storage and token bucket algorithm

**Configuration:**
```bash
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=          # Optional
REDIS_DB=0
REDIS_POOL_SIZE=10
```

**Installation:**
```bash
# Docker
docker run -d --name redis -p 6379:6379 redis:latest

# Native
apt-get install redis-server
systemctl start redis
```

**Verification:**
```bash
redis-cli ping
# Expected: PONG
```

**Notes:**
- Required for rate limiting functionality
- Without Redis, rate limiting will fail
- Can use Redis cluster for production (REDIS_CLUSTER_ENABLED=true)

---

### 2. MySQL 8.0

**Purpose:** Database for API keys, routes, service instances, audit logs

**Configuration:**
```bash
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=gateway_user
MYSQL_PASSWORD=gateway_password
MYSQL_DATABASE=gateway_db
MYSQL_POOL_SIZE=10
MYSQL_MAX_OVERFLOW=20
```

**Installation:**
```bash
# Docker
docker run -d --name mysql -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=rootpass \
  -e MYSQL_DATABASE=gateway_db \
  -e MYSQL_USER=gateway_user \
  -e MYSQL_PASSWORD=gateway_password \
  mysql:8.0

# Native
apt-get install mysql-server
systemctl start mysql
```

**Database Initialization:**
```bash
# Automatic
python scripts/database/init_database.py

# Manual
mysql -u root -p < scripts/database/init_database.sql
```

**Verification:**
```bash
mysql -u gateway_user -p -h localhost -e 'SELECT 1'
```

**Notes:**
- Required for API key storage and database operations
- Must initialize database schema before use
- Can use MySQL cluster for production (MYSQL_CLUSTER_ENABLED=true)

---

## Optional Services (Based on Configuration)

### 3. Service Discovery

Choose one: **Nacos**, **Consul**, **etcd**, or **Static**

#### Option A: Nacos (Default)

**Purpose:** Service instance discovery and registration

**Configuration:**
```bash
SERVICE_DISCOVERY_TYPE=nacos
NACOS_SERVER_ADDRESSES=localhost:8848
NACOS_NAMESPACE=public
NACOS_GROUP=DEFAULT_GROUP
```

**Installation:**
```bash
docker run -d --name nacos -p 8848:8848 nacos/nacos-server:latest
```

**Verification:**
```bash
curl http://localhost:8848/nacos/v1/console/health
```

#### Option B: Consul

**Configuration:**
```bash
SERVICE_DISCOVERY_TYPE=consul
CONSUL_HOST=localhost
CONSUL_PORT=8500
```

**Installation:**
```bash
docker run -d --name consul -p 8500:8500 consul:latest
```

#### Option C: etcd

**Configuration:**
```bash
SERVICE_DISCOVERY_TYPE=etcd
ETCD_HOST=localhost
ETCD_PORT=2379
```

**Installation:**
```bash
docker run -d --name etcd -p 2379:2379 quay.io/coreos/etcd:latest
```

#### Option D: Static (No External Service)

**Configuration:**
```bash
SERVICE_DISCOVERY_TYPE=static
```

**Notes:**
- Uses `config/services.yaml` file
- No external service required
- Good for development and testing

---

### 4. Jaeger (Distributed Tracing)

**Purpose:** Distributed tracing for request tracking

**Configuration:**
```bash
TRACING_ENABLED=true
JAEGER_AGENT_HOST=localhost
JAEGER_AGENT_PORT=6831
```

**Installation:**
```bash
docker run -d --name jaeger \
  -p 6831:6831/udp \
  -p 16686:16686 \
  jaegertracing/all-in-one:latest
```

**UI Access:**
```
http://localhost:16686
```

**Verification:**
```bash
curl http://localhost:16686
```

**Notes:**
- Optional but recommended for production
- Can be disabled with TRACING_ENABLED=false
- UI available at port 16686

---

### 5. Prometheus (Monitoring)

**Purpose:** Metrics collection and monitoring

**Configuration:**
```bash
PROMETHEUS_ENABLED=true
METRICS_PORT=9090
```

**Installation:**
```bash
docker run -d --name prometheus -p 9090:9090 prom/prometheus:latest
```

**Metrics Endpoint:**
```
http://gateway-service:9090/metrics
```

**Notes:**
- Optional but recommended for production
- Metrics exposed at /metrics endpoint
- Can be disabled with PROMETHEUS_ENABLED=false

---

## Backend Services (Required for Routing)

These services must be running and registered with service discovery:

### Project Service
- **Routes:** `/projects`, `/projects/{project_id}`
- **Expected Instances:** `http://project-service-1:8000`, `http://project-service-2:8000`
- **Health Check:** `/health`

### Auth Service
- **Routes:** `/auth/login`, `/auth/logout`, `/auth/register`, `/auth/refresh`
- **Expected Instances:** `http://auth-service-1:8000`, `http://auth-service-2:8000`
- **Health Check:** `/health`

### ECS Service
- **Routes:** `/ecs`, `/ecs/{ecs_id}`
- **Expected Instances:** `http://ecs-service-1:8000`
- **Health Check:** `/health`

### Dashboard Service
- **Routes:** `/dashboard`
- **Expected Instances:** `http://dashboard-service-1:8000`
- **Health Check:** `/health`

**Notes:**
- All backend services must implement `/health` endpoint
- Services must be registered with service discovery
- Gateway will route requests based on `config/routes.yaml`

---

## Cluster Mode Services (Optional)

Only required when `DEPLOYMENT_MODE=cluster`:

### Redis Cluster
```bash
REDIS_CLUSTER_ENABLED=true
REDIS_CLUSTER_NODES=node1:6379,node2:6379,node3:6379
```

### MySQL Cluster
```bash
MYSQL_CLUSTER_ENABLED=true
MYSQL_CLUSTER_NODES=db1:3306,db2:3306,db3:3306
MYSQL_CLUSTER_READ_REPLICAS=replica1:3306,replica2:3306
MYSQL_CLUSTER_WRITE_NODE=db1:3306
```

### Nacos Cluster
```bash
NACOS_CLUSTER_ENABLED=true
NACOS_CLUSTER_NODES=nacos1:8848,nacos2:8848,nacos3:8848
```

---

## Pre-Startup Checklist

Use this checklist before starting the gateway service:

- [ ] Python 3.10+ installed
- [ ] Python dependencies installed (`pip install -r requirements.txt`)
- [ ] Redis running and accessible
- [ ] MySQL running and accessible
- [ ] Database initialized (`python scripts/database/init_database.py`)
- [ ] Service discovery configured and running (if not using static)
- [ ] Backend services running and registered
- [ ] Environment variables configured (`.env` file)
- [ ] Log directory exists and writable
- [ ] Jaeger running (optional, for tracing)
- [ ] Prometheus configured (optional, for monitoring)

---

## Verification Script

Run the verification script to check all services:

```bash
python scripts/verify_external_services.py
```

This script will check:
- ✅ Redis connection
- ✅ MySQL connection
- ✅ Database schema initialization
- ✅ Service discovery availability
- ✅ Backend services health
- ✅ Jaeger availability (optional)
- ✅ Log directory writability

---

## Quick Start with Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  redis:
    image: redis:latest
    ports:
      - "6379:6379"
  
  mysql:
    image: mysql:8.0
    ports:
      - "3306:3306"
    environment:
      MYSQL_ROOT_PASSWORD: rootpass
      MYSQL_DATABASE: gateway_db
      MYSQL_USER: gateway_user
      MYSQL_PASSWORD: gateway_password
  
  nacos:
    image: nacos/nacos-server:latest
    ports:
      - "8848:8848"
  
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "6831:6831/udp"
      - "16686:16686"
```

Start all services:
```bash
docker-compose up -d
```

---

## Configuration Files

All configuration is done via environment variables in `.env` files:

- `.env` - Default environment
- `.env.dev` - Development environment
- `.env.prod` - Production environment

See `config/external_services.yaml` for complete configuration reference.

---

## Troubleshooting

### Redis Connection Failed
- Check Redis is running: `redis-cli ping`
- Verify REDIS_HOST and REDIS_PORT in .env
- Check firewall rules

### MySQL Connection Failed
- Check MySQL is running: `systemctl status mysql`
- Verify credentials in .env
- Ensure database exists: `mysql -u root -p -e 'SHOW DATABASES'`
- Run database initialization: `python scripts/database/init_database.py`

### Service Discovery Not Working
- Verify service discovery type in .env
- Check service discovery is running
- For static mode, verify `config/services.yaml` exists
- Check network connectivity

### Backend Services Not Found
- Verify backend services are running
- Check service registration with service discovery
- Verify `config/services.yaml` has correct service URLs
- Check backend service health endpoints

---

## Summary

**Minimum Required:**
1. Redis (for rate limiting)
2. MySQL (for database)
3. Backend services (for routing)

**Recommended:**
4. Service Discovery (Nacos/Consul/etcd)
5. Jaeger (for tracing)
6. Prometheus (for monitoring)

**For Production:**
- Use cluster mode for high availability
- Configure Redis cluster
- Configure MySQL cluster
- Set up proper monitoring and alerting

