-- Create yahoo_company_info table
CREATE TABLE IF NOT EXISTS yahoo_company_info (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL UNIQUE,
    industry VARCHAR(100),
    sector VARCHAR(100),
    company_name VARCHAR(200),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_symbol FOREIGN KEY (symbol) REFERENCES symbols(symbol) ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_yahoo_company_info_symbol ON yahoo_company_info(symbol);
CREATE INDEX IF NOT EXISTS idx_yahoo_company_info_industry ON yahoo_company_info(industry);
CREATE INDEX IF NOT EXISTS idx_yahoo_company_info_sector ON yahoo_company_info(sector);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_yahoo_company_info_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_yahoo_company_info_updated_at
    BEFORE UPDATE ON yahoo_company_info
    FOR EACH ROW
    EXECUTE FUNCTION update_yahoo_company_info_updated_at();

-- Add comments
COMMENT ON TABLE yahoo_company_info IS 'Stores company information from Yahoo Finance';
COMMENT ON COLUMN yahoo_company_info.id IS 'Primary key';
COMMENT ON COLUMN yahoo_company_info.symbol IS 'Stock symbol (foreign key to symbols table)';
COMMENT ON COLUMN yahoo_company_info.industry IS 'Company industry';
COMMENT ON COLUMN yahoo_company_info.sector IS 'Company sector';
COMMENT ON COLUMN yahoo_company_info.company_name IS 'Full company name';
COMMENT ON COLUMN yahoo_company_info.created_at IS 'Timestamp when record was created';
COMMENT ON COLUMN yahoo_company_info.updated_at IS 'Timestamp when record was last updated'; 