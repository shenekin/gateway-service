-- Database initialization script for gateway service
-- This script creates the database and required tables
-- Usage: mysql -u root -p < init_database.sql

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS gateway_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Use the database
USE gateway_db;

-- Table: api_keys
-- Stores API keys for authentication
CREATE TABLE IF NOT EXISTS api_keys (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    api_key VARCHAR(255) NOT NULL UNIQUE COMMENT 'API key value (hashed)',
    api_key_hash VARCHAR(255) NOT NULL COMMENT 'Hashed API key',
    user_id VARCHAR(100) NOT NULL COMMENT 'User identifier',
    tenant_id VARCHAR(100) COMMENT 'Tenant identifier',
    name VARCHAR(255) COMMENT 'API key name/description',
    permissions TEXT COMMENT 'Comma-separated list of permissions',
    rate_limit_per_minute INT DEFAULT 100 COMMENT 'Rate limit per minute',
    rate_limit_per_hour INT DEFAULT 1000 COMMENT 'Rate limit per hour',
    is_active BOOLEAN DEFAULT TRUE COMMENT 'Whether API key is active',
    expires_at DATETIME COMMENT 'Expiration timestamp',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update timestamp',
    created_by VARCHAR(100) COMMENT 'User who created the key',
    INDEX idx_api_key_hash (api_key_hash),
    INDEX idx_user_id (user_id),
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_is_active (is_active),
    INDEX idx_expires_at (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='API keys for authentication';

-- Table: routes
-- Stores route configurations
CREATE TABLE IF NOT EXISTS routes (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    path VARCHAR(500) NOT NULL COMMENT 'Route path pattern',
    service_name VARCHAR(100) NOT NULL COMMENT 'Target service name',
    methods VARCHAR(100) NOT NULL COMMENT 'Comma-separated HTTP methods',
    auth_required BOOLEAN DEFAULT TRUE COMMENT 'Whether authentication is required',
    rate_limit INT DEFAULT 100 COMMENT 'Rate limit per minute',
    timeout INT DEFAULT 30 COMMENT 'Request timeout in seconds',
    strip_prefix BOOLEAN DEFAULT FALSE COMMENT 'Strip path prefix when forwarding',
    rewrite_path VARCHAR(500) COMMENT 'Path rewrite pattern',
    priority INT DEFAULT 0 COMMENT 'Route priority for matching',
    is_active BOOLEAN DEFAULT TRUE COMMENT 'Whether route is active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update timestamp',
    UNIQUE KEY uk_path_methods (path, methods),
    INDEX idx_service_name (service_name),
    INDEX idx_is_active (is_active),
    INDEX idx_priority (priority)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Route configurations';

-- Table: service_instances
-- Stores service instance information
CREATE TABLE IF NOT EXISTS service_instances (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL COMMENT 'Service name',
    instance_url VARCHAR(500) NOT NULL COMMENT 'Service instance URL',
    instance_id VARCHAR(100) COMMENT 'Instance identifier',
    weight INT DEFAULT 1 COMMENT 'Load balancing weight',
    is_healthy BOOLEAN DEFAULT TRUE COMMENT 'Health status',
    health_check_path VARCHAR(200) DEFAULT '/health' COMMENT 'Health check path',
    health_check_interval INT DEFAULT 30 COMMENT 'Health check interval in seconds',
    last_health_check DATETIME COMMENT 'Last health check timestamp',
    failure_count INT DEFAULT 0 COMMENT 'Consecutive failure count',
    metadata TEXT COMMENT 'Additional metadata (JSON)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update timestamp',
    UNIQUE KEY uk_service_url (service_name, instance_url),
    INDEX idx_service_name (service_name),
    INDEX idx_is_healthy (is_healthy),
    INDEX idx_last_health_check (last_health_check)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Service instance information';

-- Table: rate_limit_records
-- Stores rate limiting records
CREATE TABLE IF NOT EXISTS rate_limit_records (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    identifier VARCHAR(255) NOT NULL COMMENT 'Rate limit identifier (user_id, ip, api_key)',
    window_type VARCHAR(20) NOT NULL COMMENT 'Time window type (minute, hour, day)',
    route_path VARCHAR(500) COMMENT 'Route path',
    request_count INT DEFAULT 0 COMMENT 'Request count in current window',
    window_start DATETIME NOT NULL COMMENT 'Window start timestamp',
    window_end DATETIME NOT NULL COMMENT 'Window end timestamp',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update timestamp',

    UNIQUE KEY uk_identifier_window (
        identifier(191),
        window_type,
        route_path(191),
        window_start
    ),
    INDEX idx_identifier (identifier(191)),
    INDEX idx_window_start (window_start),
    INDEX idx_window_end (window_end)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Rate limiting records';


-- Table: circuit_breaker_states
-- Stores circuit breaker states
CREATE TABLE IF NOT EXISTS circuit_breaker_states (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL COMMENT 'Service name',
    state VARCHAR(20) NOT NULL COMMENT 'Circuit breaker state (closed, open, half_open)',
    failure_count INT DEFAULT 0 COMMENT 'Current failure count',
    success_count INT DEFAULT 0 COMMENT 'Current success count',
    last_failure_time DATETIME COMMENT 'Last failure timestamp',
    last_state_change DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Last state change timestamp',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update timestamp',
    UNIQUE KEY uk_service_name (service_name),
    INDEX idx_state (state),
    INDEX idx_last_failure_time (last_failure_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Circuit breaker states';

-- Table: audit_logs
-- Stores audit logs for gateway operations
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    request_id VARCHAR(100) NOT NULL COMMENT 'Request identifier',
    trace_id VARCHAR(100) COMMENT 'Trace identifier',
    user_id VARCHAR(100) COMMENT 'User identifier',
    tenant_id VARCHAR(100) COMMENT 'Tenant identifier',
    method VARCHAR(10) NOT NULL COMMENT 'HTTP method',
    path VARCHAR(500) NOT NULL COMMENT 'Request path',
    service_name VARCHAR(100) COMMENT 'Target service name',
    status_code INT COMMENT 'Response status code',
    duration_ms INT COMMENT 'Request duration in milliseconds',
    client_ip VARCHAR(50) COMMENT 'Client IP address',
    user_agent VARCHAR(500) COMMENT 'User agent string',
    error_message TEXT COMMENT 'Error message if any',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
    INDEX idx_request_id (request_id),
    INDEX idx_trace_id (trace_id),
    INDEX idx_user_id (user_id),
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_service_name (service_name),
    INDEX idx_created_at (created_at),
    INDEX idx_status_code (status_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Audit logs for gateway operations';

-- Insert default route configurations
INSERT INTO routes (path, service_name, methods, auth_required, rate_limit, timeout, priority) VALUES
('/health', 'internal', 'GET', FALSE, 1000, 5, 1000),
('/ready', 'internal', 'GET', FALSE, 1000, 5, 1000),
('/metrics', 'internal', 'GET', FALSE, 1000, 5, 1000)
ON DUPLICATE KEY UPDATE updated_at = CURRENT_TIMESTAMP;

-- Create indexes for better performance
CREATE INDEX idx_routes_path_prefix ON routes(path(100));
CREATE INDEX idx_audit_logs_date_range ON audit_logs(created_at, status_code);

