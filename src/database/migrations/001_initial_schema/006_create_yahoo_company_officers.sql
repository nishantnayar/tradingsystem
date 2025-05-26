-- Create yahoo_company_officers table
CREATE TABLE IF NOT EXISTS yahoo_company_officers (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    name VARCHAR(200),
    title VARCHAR(200),
    age INTEGER,
    year_born INTEGER,
    fiscal_year INTEGER,
    total_pay BIGINT,
    exercised_value BIGINT,
    unexercised_value BIGINT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_symbol FOREIGN KEY (symbol) REFERENCES symbols(symbol) ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_yahoo_company_officers_symbol ON yahoo_company_officers(symbol);
CREATE INDEX IF NOT EXISTS idx_yahoo_company_officers_name ON yahoo_company_officers(name);
CREATE INDEX IF NOT EXISTS idx_yahoo_company_officers_title ON yahoo_company_officers(title);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_yahoo_company_officers_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_yahoo_company_officers_updated_at
    BEFORE UPDATE ON yahoo_company_officers
    FOR EACH ROW
    EXECUTE FUNCTION update_yahoo_company_officers_updated_at();

-- Add comments
COMMENT ON TABLE yahoo_company_officers IS 'Stores company officers information from Yahoo Finance';
COMMENT ON COLUMN yahoo_company_officers.id IS 'Primary key';
COMMENT ON COLUMN yahoo_company_officers.symbol IS 'Stock symbol (foreign key to symbols table)';
COMMENT ON COLUMN yahoo_company_officers.name IS 'Officer name';
COMMENT ON COLUMN yahoo_company_officers.title IS 'Officer title/position';
COMMENT ON COLUMN yahoo_company_officers.age IS 'Officer age';
COMMENT ON COLUMN yahoo_company_officers.year_born IS 'Year the officer was born';
COMMENT ON COLUMN yahoo_company_officers.fiscal_year IS 'Fiscal year of the compensation data';
COMMENT ON COLUMN yahoo_company_officers.total_pay IS 'Total compensation';
COMMENT ON COLUMN yahoo_company_officers.exercised_value IS 'Value of exercised stock options';
COMMENT ON COLUMN yahoo_company_officers.unexercised_value IS 'Value of unexercised stock options';
COMMENT ON COLUMN yahoo_company_officers.created_at IS 'Timestamp when record was created';
COMMENT ON COLUMN yahoo_company_officers.updated_at IS 'Timestamp when record was last updated'; 