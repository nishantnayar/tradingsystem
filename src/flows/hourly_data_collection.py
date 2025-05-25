from datetime import datetime, timedelta
from typing import List, Dict, Optional
import sys
from pathlib import Path

import pandas as pd
from prefect import flow, task, get_run_logger
from prefect_dask import DaskTaskRunner
from loguru import logger
from sqlalchemy import text

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Configure logging
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG"  # Set to DEBUG level
)

from src.data.data_manager import DataManager
from src.data.symbol_manager import SymbolManager
from src.data.sources.alpaca_source import AlpacaDataSource
from src.database.db_manager import DatabaseManager
from src.utils.config import get_config


def generate_flow_run_name(flow_prefix: str) -> str:
    """Generate a descriptive flow run name for debugging."""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    return f"{flow_prefix}-{timestamp}"


@task(retries=3, retry_delay_seconds=60)
def collect_market_data() -> Dict[str, pd.DataFrame]:
    """Task to collect market data for all active symbols."""
    logger = get_run_logger()
    logger.info("Starting data collection")
    
    try:
        # Get active symbols
        symbols = SymbolManager.get_active_symbols()
        logger.debug(f"Retrieved active symbols: {symbols}")  # Debug log
        if not symbols:
            logger.warning("No active symbols found")
            return {}

        # For testing, only process one symbol
        test_symbol = "AAPL"  # Using AAPL as test symbol
        logger.info(f"Test mode: Only processing symbol {test_symbol}")
        symbols = [test_symbol]

        # Initialize Alpaca data source
        alpaca_source = AlpacaDataSource()
        logger.debug("Initialized Alpaca data source")  # Debug log
        
        # Collect data for test symbol
        data = alpaca_source.get_multiple_symbols(
            symbols=symbols,
            interval="1h",  # Hourly data
            lookback_days=1  # Get last 24 hours of data
        )
        
        # Detailed logging for collected data
        for symbol, df in data.items():
            logger.debug(f"Data for {symbol}: {len(df)} rows")
            logger.debug(f"DataFrame columns: {df.columns.tolist()}")
            if not df.empty:
                logger.debug(f"Sample data for {symbol}:\n{df.head(1)}")
                logger.debug(f"DataFrame info:\n{df.info()}")
                logger.debug(f"DataFrame index type: {type(df.index)}")
                logger.debug(f"DataFrame index values: {df.index.tolist()}")
            else:
                logger.warning(f"Empty DataFrame received for {symbol}")
        
        logger.info(f"Data collection completed successfully for {len(data)} symbols")
        return data
        
    except Exception as e:
        logger.error(f"Error collecting data: {str(e)}")
        raise


@task
def store_market_data(data: Dict[str, pd.DataFrame]):
    """Task to store collected market data in the database."""
    logger = get_run_logger()
    if not data:
        logger.warning("No data to store")
        return

    try:
        db = DatabaseManager()
        logger.debug("Initialized database connection")  # Debug log
        
        with db.get_session() as session:
            total_rows = 0
            for symbol, df in data.items():
                logger.debug(f"Processing data for symbol: {symbol}")  # Debug log
                logger.debug(f"DataFrame info for {symbol}:\n{df.info()}")  # Add DataFrame info
                logger.debug(f"DataFrame head for {symbol}:\n{df.head()}")  # Add DataFrame head
                
                if df.empty:
                    logger.warning(f"No data to store for symbol {symbol}")
                    continue
                
                # Reset index to make timestamp a column
                df = df.reset_index()
                logger.debug(f"DataFrame after reset_index for {symbol}:\n{df.head()}")
                
                for _, row in df.iterrows():
                    try:
                        # Debug log the row data
                        logger.debug(f"Processing row for {symbol}: {row.to_dict()}")
                        
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
                        
                        # Convert timestamp to datetime if it's not already
                        timestamp = pd.to_datetime(row['timestamp'])
                        logger.debug(f"Timestamp value: {timestamp}")
                            
                        params = {
                            'symbol': symbol,
                            'timestamp': timestamp,
                            'open': float(row['open']),
                            'high': float(row['high']),
                            'low': float(row['low']),
                            'close': float(row['close']),
                            'volume': int(row['volume'])
                        }
                        
                        logger.debug(f"Executing SQL with params: {params}")  # Debug log
                        result = session.execute(stmt, params)
                        total_rows += 1
                        
                    except Exception as e:
                        logger.error(f"Error storing data for {symbol}: {str(e)}")
                        logger.error(f"Row data: {row.to_dict()}")  # Debug log
                        continue
                        
            try:
                logger.debug(f"Committing {total_rows} rows to database")  # Debug log
                session.commit()
                logger.info(f"Data storage completed successfully. Total rows inserted/updated: {total_rows}")
            except Exception as e:
                logger.error(f"Error committing data to database: {str(e)}")
                session.rollback()
                raise
        
    except Exception as e:
        logger.error(f"Error storing data: {str(e)}")
        raise


@task
def run_model_inference(symbols: List[str]):
    """Task to run ML model inference on collected data."""
    logger = get_run_logger()
    try:
        # TODO: Implement ML model inference
        # This will be implemented later
        logger.info(f"Model inference completed for {len(symbols)} symbols")
        
    except Exception as e:
        logger.error(f"Error in model inference: {str(e)}")
        raise


@task
def make_trading_decisions(symbols: List[str]):
    """Task to make trading decisions based on model output."""
    logger = get_run_logger()
    try:
        # TODO: Implement trading decision logic
        # This will be implemented later
        logger.info(f"Trading decisions completed for {len(symbols)} symbols")
        
    except Exception as e:
        logger.error(f"Error in trading decisions: {str(e)}")
        raise


@flow(
    name="Hourly Data Collection",
    flow_run_name=lambda: generate_flow_run_name("hourly-data"),
    task_runner=DaskTaskRunner(cluster_kwargs={"n_workers": 3, "processes": False})
)
def hourly_data_collection_flow():
    """Main flow for hourly data collection and processing."""
    logger = get_run_logger()
    logger.info("Starting hourly data collection flow")
    
    try:
        # Get active symbols
        symbols = SymbolManager.get_active_symbols()
        if not symbols:
            logger.warning("No active symbols found")
            return
            
        # Collect market data
        data = collect_market_data()
        
        # Store market data
        store_market_data(data)
        
        # Run model inference
        run_model_inference(symbols)
        
        # Make trading decisions
        make_trading_decisions(symbols)
        
        logger.info("Hourly data collection flow completed successfully")
        
    except Exception as e:
        logger.error(f"Error in hourly data collection flow: {str(e)}")
        raise


if __name__ == "__main__":
    hourly_data_collection_flow() 