-- Update audit_logs table to support authentication event logging
-- This script adds event_type, ip_address, user_agent, and details columns

USE gateway_db;

-- Add new columns if they don't exist
ALTER TABLE audit_logs 
ADD COLUMN IF NOT EXISTS event_type VARCHAR(50) COMMENT 'Event type (login, refresh, revoke)',
ADD COLUMN IF NOT EXISTS ip_address VARCHAR(50) COMMENT 'Client IP address',
ADD COLUMN IF NOT EXISTS user_agent VARCHAR(500) COMMENT 'User agent string',
ADD COLUMN IF NOT EXISTS details TEXT COMMENT 'Additional event details (JSON)';

-- Create index on event_type for faster queries
CREATE INDEX IF NOT EXISTS idx_event_type ON audit_logs(event_type);

-- Create index on event_type and created_at for time-based queries
CREATE INDEX IF NOT EXISTS idx_event_type_created_at ON audit_logs(event_type, created_at);

