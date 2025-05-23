from datetime import datetime
from typing import List, Optional

from loguru import logger
from prefect import flow, task
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.data.sources.alpaca_source import AlpacaDataSource
from src.data.symbol_manager import SymbolManager
from src.database.db_manager import DatabaseManager
from src.database.models import MarketData


@task(retries=3, retry_delay_seconds=60)
def collect_market_data() -> dict:
    """Task to collect market data for all active symbols."""
    logger.info("Starting data collection")
    
    try:
        # Get active symbols
        symbols = SymbolManager.get_active_symbols()
        if not symbols:
            logger.warning("No active symbols found")
            return {}

        # Collect data from Alpaca
        alpaca_source = AlpacaDataSource()
        data = alpaca_source.get_multiple_symbols(symbols)
        
        logger.info(f"Data collection completed successfully for {len(data)} symbols")
        return data
        
    except Exception as e:
        logger.error(f"Error collecting data: {str(e)}")
        raise


@task
def store_market_data(data: dict):
    """Task to store collected market data in the database."""
    if not data:
        logger.warning("No data to store")
        return

    db = DatabaseManager()
    with db.get_session() as session:
        for symbol, df in data.items():
            if df.empty:
                logger.warning(f"No data to store for symbol {symbol}")
                continue
                
            for _, row in df.iterrows():
                try:
                    # Use upsert operation to prevent duplicates
                    stmt = text("""
                        INSERT INTO market_data (symbol, timestamp, open, high, low, close, volume)
                        VALUES (:symbol, :timestamp, :open, :high, :low, :close, :volume)
                        ON CONFLICT (symbol, timestamp) 
                        DO UPDATE SET
                            open = EXCLUDED.open,
                            high = EXCLUDED.high,
                            low = EXCLUDED.low,
                            close = EXCLUDED.close,
                            volume = EXCLUDED.volume
                    """)
                    session.execute(
                        stmt,
                        {
                            'symbol': symbol,
                            'timestamp': row['timestamp'],
                            'open': float(row['open']),
                            'high': float(row['high']),
                            'low': float(row['low']),
                            'close': float(row['close']),
                            'volume': int(row['volume'])
                        }
                    )
                except Exception as e:
                    logger.error(f"Error storing data for {symbol}: {str(e)}")
                    continue
                    
        try:
            session.commit()
            logger.info("Data storage completed successfully")
        except Exception as e:
            logger.error(f"Error committing data to database: {str(e)}")
            session.rollback()
            raise


@flow(name="Market Data Collection")
def market_data_collection_flow():
    """Flow for collecting and storing market data."""
    data = collect_market_data()
    store_market_data(data)


class DataManager:
    """Manages data collection and storage for the trading system."""

    def get_latest_data(self, symbol: str) -> Optional[dict]:
        """Get the latest data for a symbol."""
        try:
            # Check if symbol is active
            symbol_info = SymbolManager.get_symbol_info(symbol)
            if not symbol_info or not symbol_info.is_active:
                logger.warning(f"Symbol {symbol} is not active")
                return None

            alpaca_source = AlpacaDataSource()
            return alpaca_source.get_latest_data(symbol)
        except Exception as e:
            logger.error(f"Error getting latest data for {symbol}: {str(e)}")
            return None 