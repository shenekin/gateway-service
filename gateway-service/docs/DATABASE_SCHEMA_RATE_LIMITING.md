# Database Schema for Rate Limiting

**Date:** 2025-12-25  
**Purpose:** Documentation for rate limiting database tables and usage

## Overview

The gateway service uses both Redis and MySQL for rate limiting:

- **Redis**: Primary storage for rate limit counters (fast, in-memory) - *Used for fast rate limit checking*
- **MySQL**: Persistent storage for rate limit records (audit and analytics) - *Added: 2025-12-25*

**Integration Architecture:**
- Redis handles fast in-memory rate limit checking (primary)
- MySQL stores rate limit records for audit, analytics, and historical tracking (secondary)
- Records are stored asynchronously to avoid blocking rate limit checks
- Rate limiting continues to work even if MySQL is unavailable (fail-safe)

## Rate Limiting Tables

### Table: `rate_limit_records`

**Purpose:** Stores rate limiting records for audit, analytics, and historical tracking

**Schema:**
```sql
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
```

**Identifier Format:**
- `user:{user_id}` - For authenticated users (e.g., `user:123`)
- `login:{username}` - For login endpoints before authentication (e.g., `login:john_doe`)
- `login:{email}` - For login endpoints using email (e.g., `login:john@example.com`)
- `api_key:{key}` - For API key authentication (e.g., `api_key:abc123`)
- `ip:{ip_address}` - Fallback for unauthenticated requests (e.g., `ip:192.168.1.1`)

**Example Records:**
```sql
-- User-based rate limit record
INSERT INTO rate_limit_records 
(identifier, window_type, route_path, request_count, window_start, window_end)
VALUES 
('user:123', 'minute', '/projects', 45, '2025-12-25 10:00:00', '2025-12-25 10:01:00');

-- Login-based rate limit record
INSERT INTO rate_limit_records 
(identifier, window_type, route_path, request_count, window_start, window_end)
VALUES 
('login:john_doe', 'minute', '/auth/login', 3, '2025-12-25 10:00:00', '2025-12-25 10:01:00');

-- IP-based rate limit record (fallback)
INSERT INTO rate_limit_records 
(identifier, window_type, route_path, request_count, window_start, window_end)
VALUES 
('ip:192.168.1.1', 'minute', '/public', 10, '2025-12-25 10:00:00', '2025-12-25 10:01:00');
```

## Per-User Rate Limiting

### How It Works

1. **For Authenticated Requests:**
   - User ID is extracted from `request.state.user_id` (set after authentication)
   - Redis key format: `rate_limit:user:{user_id}:{window}:{route_path}`
   - Each user has independent rate limit counter

2. **For Login Endpoints:**
   - Username or email is extracted from request body before authentication
   - Redis key format: `rate_limit:login:{username}:{window}:{route_path}`
   - Ensures per-user rate limiting even before authentication completes

3. **For API Key Requests:**
   - API key is extracted from headers
   - Redis key format: `rate_limit:api_key:{key}:{window}:{route_path}`
   - Each API key has independent rate limit

4. **Fallback (IP Address):**
   - Used only when no user identifier is available
   - Redis key format: `rate_limit:ip:{ip_address}:{window}:{route_path}`
   - Should be avoided for authenticated requests

### Example Redis Keys

```
# User-based (authenticated)
rate_limit:user:123:minute:/projects
rate_limit:user:456:minute:/projects

# Login-based (before authentication)
rate_limit:login:john_doe:minute:/auth/login
rate_limit:login:jane@example.com:minute:/auth/login

# API key-based
rate_limit:api_key:abc123:minute:/api/v1/data

# IP-based (fallback)
rate_limit:ip:192.168.1.1:minute:/public
```

## Database Initialization

### Automatic Initialization

```bash
python scripts/database/init_database.py
```

### Manual Initialization

```bash
mysql -u root -p < scripts/database/init_database.sql
```

### Verification

```sql
-- Check if table exists
SHOW TABLES LIKE 'rate_limit_records';

-- Check table structure
DESCRIBE rate_limit_records;

-- Check indexes
SHOW INDEXES FROM rate_limit_records;
```

## Usage Examples

### Query Rate Limit Records by User

```sql
-- Get rate limit records for a specific user
SELECT * FROM rate_limit_records 
WHERE identifier = 'user:123' 
ORDER BY window_start DESC 
LIMIT 10;
```

### Query Rate Limit Records by Route

```sql
-- Get rate limit records for a specific route
SELECT identifier, window_type, request_count, window_start 
FROM rate_limit_records 
WHERE route_path = '/auth/login' 
ORDER BY window_start DESC;
```

### Query Rate Limit Violations

```sql
-- Find users who exceeded rate limits
SELECT identifier, route_path, request_count, window_start 
FROM rate_limit_records 
WHERE request_count >= 100  -- Assuming limit is 100
ORDER BY request_count DESC;
```

### Cleanup Old Records

```sql
-- Delete records older than 30 days
DELETE FROM rate_limit_records 
WHERE window_end < DATE_SUB(NOW(), INTERVAL 30 DAY);
```

## Performance Considerations

1. **Indexes:**
   - `idx_identifier`: Fast lookup by user/identifier
   - `idx_window_start`: Efficient time-based queries
   - `idx_window_end`: Efficient cleanup operations

2. **Partitioning:**
   - Consider partitioning by `window_start` for large datasets
   - Monthly or weekly partitions recommended

3. **Archival:**
   - Archive old records to separate table or storage
   - Keep only recent records (e.g., last 90 days) in main table

## Monitoring and Analytics

### Rate Limit Statistics

```sql
-- Top users by request count
SELECT identifier, SUM(request_count) as total_requests
FROM rate_limit_records
WHERE window_start >= DATE_SUB(NOW(), INTERVAL 1 DAY)
GROUP BY identifier
ORDER BY total_requests DESC
LIMIT 10;
```

### Rate Limit Trends

```sql
-- Request count by hour
SELECT 
    DATE_FORMAT(window_start, '%Y-%m-%d %H:00:00') as hour,
    SUM(request_count) as total_requests
FROM rate_limit_records
WHERE window_start >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY hour
ORDER BY hour;
```

## Related Tables

- **`api_keys`**: Stores API keys with rate limit configuration
- **`routes`**: Stores route configurations with rate limit settings
- **`audit_logs`**: Stores request logs including rate limit information

## Notes

- Rate limiting primarily uses Redis for performance
- MySQL table is used for audit and analytics
- Per-user rate limiting ensures fair resource allocation
- Login endpoints use username/email for identification before authentication

