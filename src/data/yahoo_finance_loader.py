"""
Yahoo Finance data loader for company information.
"""
import yfinance as yf
import pandas as pd
import time
from loguru import logger
from sqlalchemy import text
import random
from typing import Dict, Any, Optional

from src.database.db_manager import DatabaseManager
from src.data.symbol_manager import SymbolManager


class YahooFinanceDataLoader:
    def __init__(self):
        self.db = DatabaseManager()
        self.rate_limit_delay = 2  # Base delay between requests in seconds
        self.max_retries = 3  # Maximum number of retries for failed requests

    def _get_ticker_info_with_retry(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get ticker info with retry logic and rate limiting."""
        for attempt in range(self.max_retries):
            try:
                # Add random jitter to avoid synchronized requests
                jitter = random.uniform(0.5, 1.5)
                time.sleep(self.rate_limit_delay * jitter)

                # Get ticker info using fast_info for better reliability
                ticker = yf.Ticker(symbol)
                fast_info = ticker.fast_info
                
                # Get additional info from info if available
                try:
                    info = ticker.info
                    industry = info.get('industry')
                    sector = info.get('sector')
                    company_name = info.get('longName')
                except Exception:
                    # If info fails, use basic info from fast_info
                    industry = None
                    sector = None
                    company_name = fast_info.get('displayName')

                # Only return if we have at least some valid data
                if company_name or industry or sector:
                    return {
                        'symbol': symbol,
                        'industry': industry,
                        'sector': sector,
                        'company_name': company_name
                    }
                else:
                    logger.warning(f"No valid data found for {symbol}")
                    return None

            except Exception as e:
                if "429" in str(e):  # Rate limit error
                    wait_time = (attempt + 1) * 5  # Exponential backoff
                    logger.warning(f"Rate limited for {symbol}, waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Error loading data for {symbol} (attempt {attempt + 1}/{self.max_retries}): {e}")
                
                if attempt == self.max_retries - 1:
                    logger.error(f"Failed to get data for {symbol} after {self.max_retries} attempts")
                    return None

        return None

    def load_ticker_info_chunk(self, stock_symbols):
        # List to store processed data for the current chunk
        ticker_info_list = []

        for symbol in stock_symbols:
            info = self._get_ticker_info_with_retry(symbol)
            if info:
                ticker_info_list.append(info)
                logger.info(f"Successfully received data for {symbol}")

        return ticker_info_list

    def store_company_info(self, company_info_list):
        """Store company information in the database."""
        if not company_info_list:
            return

        session = None
        try:
            session = self.db.get_session().__enter__()
            
            for info in company_info_list:
                try:
                    # Only update if we have at least one non-NULL value
                    if any(info.get(field) for field in ['industry', 'sector', 'company_name']):
                        # Upsert the company information
                        stmt = text("""
                            INSERT INTO yahoo_company_info (symbol, industry, sector, company_name)
                            VALUES (:symbol, :industry, :sector, :company_name)
                            ON CONFLICT (symbol) DO UPDATE SET
                                industry = COALESCE(EXCLUDED.industry, yahoo_company_info.industry),
                                sector = COALESCE(EXCLUDED.sector, yahoo_company_info.sector),
                                company_name = COALESCE(EXCLUDED.company_name, yahoo_company_info.company_name),
                                updated_at = CURRENT_TIMESTAMP
                        """)
                        
                        session.execute(stmt, info)
                        logger.info(f"Stored company info for {info['symbol']}")
                    else:
                        logger.warning(f"Skipping {info['symbol']} - no valid data to store")
                except Exception as e:
                    logger.error(f"Error storing company info for {info['symbol']}: {e}")
                    # Don't continue with this session if we hit an error
                    raise

            session.commit()
            logger.info("Successfully committed company information to database")
        except Exception as e:
            if session:
                session.rollback()
            logger.error(f"Error in database transaction: {e}")
            raise
        finally:
            if session:
                session.close()

    def load_ticker_info(self, stock_symbols):
        # Process stocks in smaller chunks to avoid rate limits
        chunk_size = 50  # Reduced from 200 to 50
        for i in range(0, len(stock_symbols), chunk_size):
            chunk_symbols = stock_symbols[i:i + chunk_size]
            logger.info(f"Processing chunk {i // chunk_size + 1} containing {len(chunk_symbols)} symbols...")

            # Load ticker info for the current chunk
            company_info_list = self.load_ticker_info_chunk(chunk_symbols)

            # Store the company information
            if company_info_list:
                self.store_company_info(company_info_list)

            # Sleep between chunks to respect rate limits
            if i + chunk_size < len(stock_symbols):
                sleep_time = 30  # 30 seconds between chunks
                logger.info(f"Sleeping for {sleep_time} seconds before processing the next chunk...")
                time.sleep(sleep_time)

    def run(self):
        # Get active symbols from SymbolManager
        stock_symbols = SymbolManager.get_active_symbols()

        if not stock_symbols:
            logger.error("No active symbols found in the database.")
            return

        # Load ticker info
        self.load_ticker_info(stock_symbols)
        logger.info("Yahoo company data loading completed.")


if __name__ == "__main__":
    # Create an instance of the YahooFinanceDataLoader and run it
    loader = YahooFinanceDataLoader()
    loader.run()

    # # Save the resulting data to a CSV file
    if not loader.yahoo_data_df.empty:
        loader.yahoo_data_df.to_csv("ticker_info.csv", index=False)
        print("Ticker info saved to ticker_info.csv")