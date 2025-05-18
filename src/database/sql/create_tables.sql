-- Drop existing table if it exists
DROP TABLE IF EXISTS logs;

-- Create logs table
CREATE TABLE logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    level VARCHAR(10) NOT NULL,
    message TEXT NOT NULL,
    module VARCHAR(100) NOT NULL,
    function VARCHAR(100) NOT NULL,
    line_number INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_logs_timestamp ON logs(timestamp);
CREATE INDEX idx_logs_level ON logs(level);
CREATE INDEX idx_logs_module ON logs(module);

-- Add comment to table
COMMENT ON TABLE logs IS 'Application logs storage table';

-- Add comments to columns
COMMENT ON COLUMN logs.id IS 'Primary key';
COMMENT ON COLUMN logs.timestamp IS 'Timestamp of the log entry';
COMMENT ON COLUMN logs.level IS 'Log level (INFO, ERROR, etc.)';
COMMENT ON COLUMN logs.message IS 'Log message content';
COMMENT ON COLUMN logs.module IS 'Module name where log was generated';
COMMENT ON COLUMN logs.function IS 'Function name where log was generated';
COMMENT ON COLUMN logs.line_number IS 'Line number where log was generated';
COMMENT ON COLUMN logs.created_at IS 'Timestamp when log was stored in database'; 