-- Create audit_logs table for authentication event logging
-- This table stores login, refresh, and revoke events for audit and compliance

-- Use the database (adjust database name as needed)
-- For auth_service database:
USE auth_service;

-- For gateway_db database (if using separate database):
-- USE gateway_db;

-- Create audit_logs table if it doesn't exist
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL COMMENT 'Event type (login, refresh, revoke)',
    user_id VARCHAR(100) NOT NULL COMMENT 'User identifier',
    ip_address VARCHAR(50) COMMENT 'Client IP address',
    user_agent VARCHAR(500) COMMENT 'User agent string',
    details TEXT COMMENT 'Additional event details (JSON)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation timestamp',
    
    -- Indexes for better query performance
    INDEX idx_event_type (event_type),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    INDEX idx_event_type_created_at (event_type, created_at),
    INDEX idx_user_id_created_at (user_id, created_at)
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci 
  COMMENT='Audit logs for authentication events (login, refresh, revoke)';

-- If table already exists, add missing columns
ALTER TABLE audit_logs 
ADD COLUMN IF NOT EXISTS event_type VARCHAR(50) NOT NULL COMMENT 'Event type (login, refresh, revoke)' AFTER id,
ADD COLUMN IF NOT EXISTS ip_address VARCHAR(50) COMMENT 'Client IP address' AFTER user_id,
ADD COLUMN IF NOT EXISTS user_agent VARCHAR(500) COMMENT 'User agent string' AFTER ip_address,
ADD COLUMN IF NOT EXISTS details TEXT COMMENT 'Additional event details (JSON)' AFTER user_agent;

-- Create indexes if they don't exist
CREATE INDEX IF NOT EXISTS idx_event_type ON audit_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_event_type_created_at ON audit_logs(event_type, created_at);
CREATE INDEX IF NOT EXISTS idx_user_id_created_at ON audit_logs(user_id, created_at);

-- Verify table structure
DESCRIBE audit_logs;

