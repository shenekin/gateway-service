-- Create audit_logs table for authentication event logging in auth_service database
-- This table stores login, refresh, and revoke events for audit and compliance

USE auth_service;

-- Drop table if exists (for clean setup, comment out if you want to preserve existing data)
-- DROP TABLE IF EXISTS audit_logs;

-- Create audit_logs table
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

-- Verify table was created
SELECT 'audit_logs table created successfully' AS status;

-- Show table structure
DESCRIBE audit_logs;

