-- Add unique constraint to market_data table
ALTER TABLE market_data
ADD CONSTRAINT uix_market_data_symbol_timestamp 
UNIQUE (symbol, timestamp);

-- Create index to support the unique constraint
CREATE INDEX IF NOT EXISTS idx_market_data_symbol_timestamp 
ON market_data (symbol, timestamp); 