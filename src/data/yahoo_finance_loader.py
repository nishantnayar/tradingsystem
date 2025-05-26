"""
Yahoo Finance data loader for company information.
"""
import yfinance as yf
import pandas as pd
import time
from loguru import logger
from sqlalchemy import text
import random
from typing import Dict, Any, Optional, List

from src.database.db_manager import DatabaseManager
from src.data.symbol_manager import SymbolManager


class YahooFinanceDataLoader:
    def __init__(self):
        self.db = DatabaseManager()
        self.rate_limit_delay = 2  # Base delay between requests in seconds
        self.max_retries = 3  # Maximum number of retries for failed requests
        self.raw_data = []  # List to store raw ticker info
        self.columns_printed = False  # Flag to track if columns have been printed

    def _get_ticker_info_with_retry(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get ticker info with retry logic and rate limiting."""
        for attempt in range(self.max_retries):
            try:
                # Add random jitter to avoid synchronized requests
                jitter = random.uniform(0.5, 1.5)
                time.sleep(self.rate_limit_delay * jitter)

                # Get ticker info
                ticker = yf.Ticker(symbol)
                ticker_info = ticker.info

                # Store raw data for inspection
                ticker_info['symbol'] = symbol
                self.raw_data.append(ticker_info)

                # Extract company officers data before removing it
                company_officers = ticker_info.get('companyOfficers', [])
                if company_officers:
                    self.store_company_officers(symbol, company_officers)

                # Remove fields that are not in our database schema
                ticker_info.pop('companyOfficers', None)
                ticker_info.pop('underlyingSymbol', None)  # Remove underlyingSymbol field
                ticker_info.pop('firstTradeDateEpochUtc', None)  # Remove firstTradeDateEpochUtc field
                ticker_info.pop('timeZoneFullName', None)  # Remove timeZoneFullName field
                ticker_info.pop('timeZoneShortName', None)  # Remove timeZoneShortName field
                ticker_info.pop('gmtOffSetMilliseconds', None)  # Remove gmtOffSetMilliseconds field
                ticker_info.pop('uuid', None)  # Remove uuid field
                ticker_info.pop('industrySymbol', None)  # Remove industrySymbol field

                # Add symbol to the info dictionary
                ticker_info['symbol'] = symbol

                # Convert any non-serializable values to strings
                for key, value in ticker_info.items():
                    if isinstance(value, (dict, list)):
                        ticker_info[key] = str(value)

                return ticker_info

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

    def store_company_officers(self, symbol: str, officers: List[Dict[str, Any]]):
        """Store company officers information in the database."""
        if not officers:
            return

        session = None
        try:
            session = self.db.get_session().__enter__()
            
            # First, delete existing officers for this symbol
            delete_stmt = text("DELETE FROM yahoo_company_officers WHERE symbol = :symbol")
            session.execute(delete_stmt, {'symbol': symbol})
            
            # Insert new officers
            for officer in officers:
                insert_stmt = text("""
                    INSERT INTO yahoo_company_officers 
                    (symbol, name, title, age, year_born, fiscal_year, total_pay, exercised_value, unexercised_value)
                    VALUES 
                    (:symbol, :name, :title, :age, :year_born, :fiscal_year, :total_pay, :exercised_value, :unexercised_value)
                """)
                
                session.execute(insert_stmt, {
                    'symbol': symbol,
                    'name': officer.get('name'),
                    'title': officer.get('title'),
                    'age': officer.get('age'),
                    'year_born': officer.get('yearBorn'),
                    'fiscal_year': officer.get('fiscalYear'),
                    'total_pay': officer.get('totalPay'),
                    'exercised_value': officer.get('exercisedValue'),
                    'unexercised_value': officer.get('unexercisedValue')
                })
            
            session.commit()
            logger.info(f"Stored {len(officers)} company officers for {symbol}")
            
        except Exception as e:
            if session:
                session.rollback()
            logger.error(f"Error storing company officers for {symbol}: {e}")
            raise
        finally:
            if session:
                session.close()

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
                    # Create dynamic SQL statement based on available fields
                    fields = list(info.keys())
                    # Quote fields that start with numbers or contain uppercase letters
                    quoted_fields = []
                    for field in fields:
                        if field[0].isdigit() or any(c.isupper() for c in field):
                            quoted_fields.append(f'"{field}"')
                        else:
                            quoted_fields.append(field)
                    placeholders = [f":{field}" for field in fields]
                    
                    # Create the INSERT statement
                    insert_stmt = f"""
                        INSERT INTO yahoo_company_info ({', '.join(quoted_fields)})
                        VALUES ({', '.join(placeholders)})
                        ON CONFLICT (symbol) DO UPDATE SET
                    """
                    
                    # Create the UPDATE part of the statement
                    update_parts = []
                    for field in fields:
                        if field != 'symbol':  # Skip symbol in UPDATE part
                            quoted_field = f'"{field}"' if field[0].isdigit() or any(c.isupper() for c in field) else field
                            update_parts.append(f"{quoted_field} = COALESCE(EXCLUDED.{quoted_field}, yahoo_company_info.{quoted_field})")
                    
                    insert_stmt += ', '.join(update_parts)
                    insert_stmt += ", updated_at = CURRENT_TIMESTAMP"
                    
                    # Execute the statement
                    session.execute(text(insert_stmt), info)
                    logger.info(f"Stored company info for {info['symbol']}")
                    
                except Exception as e:
                    logger.error(f"Error storing company info for {info['symbol']}: {e}")
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

    # Save the raw data to CSV for inspection
    if loader.raw_data:
        raw_df = pd.DataFrame(loader.raw_data)
        raw_df.to_csv("yahoo_raw_data.csv", index=False)
        print("\nRaw ticker info saved to yahoo_raw_data.csv")