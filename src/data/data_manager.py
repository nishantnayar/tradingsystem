from datetime import datetime, timedelta
from typing import List, Optional, Dict
import os
import platform
import sys
from prefect.blocks.system import Secret

from loguru import logger
from prefect import flow, task
from prefect.context import get_run_context
from sqlalchemy.orm import Session
from sqlalchemy import text
import pandas as pd
from prefect_dask import DaskTaskRunner

from src.data.sources.alpaca_source import AlpacaDataSource
from src.data.symbol_manager import SymbolManager
from src.database.db_manager import DatabaseManager
from src.database.models import MarketData


async def ensure_db_credentials():
    """Ensure database credentials are set in environment variables."""
    try:
        # Get database credentials from Prefect secrets
        db_user = str(await Secret.load("db-user"))
        db_password = str(await Secret.load("db-password"))
        db_host = str(await Secret.load("db-host"))
        db_port = str(await Secret.load("db-port"))
        db_name = str(await Secret.load("db-name"))

        # Set environment variables
        os.environ["DB_USER"] = db_user
        os.environ["DB_PASSWORD"] = db_password
        os.environ["DB_HOST"] = db_host
        os.environ["DB_PORT"] = db_port
        os.environ["DB_NAME"] = db_name

        logger.debug(f"Database credentials set for host={db_host}, port={db_port}, user={db_user}, database={db_name}")
    except Exception as e:
        logger.error(f"Failed to set database credentials: {e}")
        raise


def generate_flow_run_name(flow_prefix: str) -> str:
    """Generate a descriptive flow run name for debugging.
    
    Args:
        flow_prefix: Prefix for the flow name (e.g., 'market-data-run')
        
    Returns:
        str: Flow run name in format: prefix-YYYYMMDD-HHMMSS-{context}
    """
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    
    # Get environment info for debugging
    env = os.getenv('ENVIRONMENT', 'dev')
    
    # Get active symbols count for market data flows
    try:
        # Since we can't use async here, we'll just use a placeholder
        context = "symbols-unknown"
    except Exception:
        context = "unknown-symbols"
    
    return f"{flow_prefix}-{timestamp}-{env}-{context}"


@task(retries=3, retry_delay_seconds=60)
async def collect_market_data() -> dict:
    """Task to collect market data for all active symbols."""
    logger.info("Starting data collection")
    
    try:
        # Ensure database credentials are set
        await ensure_db_credentials()
        
        # Get active symbols
        symbols = await SymbolManager.get_active_symbols()
        logger.debug(f"Retrieved active symbols: {symbols}")  # Debug log
        if not symbols:
            logger.warning("No active symbols found")
            return {}

        # Initialize Alpaca data source
        alpaca_source = AlpacaDataSource()
        logger.debug("Initialized Alpaca data source")  # Debug log
        
        # Collect data for all symbols
        data = alpaca_source.get_multiple_symbols(
            symbols=symbols,
            interval="1h",  # Hourly data
            lookback_days=10  # Get last 24 hours of data
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
async def store_market_data(data: dict):
    """Task to store collected market data in the database."""
    if not data:
        logger.warning("No data to store")
        return

    try:
        # Ensure database credentials are set
        await ensure_db_credentials()
        
        db = DatabaseManager()
        with db.get_session() as session:
            for symbol, df in data.items():
                if df.empty:
                    logger.warning(f"No data to store for symbol {symbol}")
                    continue
                    
                logger.debug(f"Processing data for {symbol}")
                logger.debug(f"DataFrame info:\n{df.info()}")
                logger.debug(f"DataFrame head:\n{df.head()}")
                
                # Reset index to make timestamp a column
                df = df.reset_index()
                logger.debug(f"DataFrame after reset_index:\n{df.head()}")
                
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
                        
                        # Convert timestamp to UTC if it has timezone info
                        timestamp = row['timestamp']
                        if hasattr(timestamp, 'tz_localize'):
                            timestamp = timestamp.tz_localize(None)
                        
                        params = {
                            'symbol': symbol,
                            'timestamp': timestamp,
                            'open': float(row['open']),
                            'high': float(row['high']),
                            'low': float(row['low']),
                            'close': float(row['close']),
                            'volume': int(row['volume'])
                        }
                        
                        logger.debug(f"Executing SQL with params: {params}")
                        session.execute(stmt, params)
                        
                    except Exception as e:
                        logger.error(f"Error storing data for {symbol}: {str(e)}")
                        logger.error(f"Row data: {row.to_dict()}")
                        continue
                        
            try:
                session.commit()
                logger.info("Data storage completed successfully")
            except Exception as e:
                logger.error(f"Error committing data to database: {str(e)}")
                session.rollback()
                raise
        
    except Exception as e:
        logger.error(f"Error storing data: {str(e)}")
        raise


@flow(name="Market Data Collection", flow_run_name=generate_flow_run_name("market-data"))
def market_data_collection_flow():
    """Flow for collecting and storing market data."""
    data = collect_market_data()
    store_market_data(data)


class DataManager:
    """Manages data collection and storage for the trading system."""

    def get_latest_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Get the latest data for a symbol."""
        try:
            # Check if symbol is active
            symbol_info = SymbolManager.get_symbol_info(symbol)
            if not symbol_info or not symbol_info.is_active:
                logger.warning(f"Symbol {symbol} is not active")
                return None

            # Get data from Alpaca
            alpaca_source = AlpacaDataSource()
            data = alpaca_source.get_latest_data(symbol)
            
            if data is not None and not data.empty:
                return data
            return None
            
        except Exception as e:
            logger.error(f"Error getting latest data for {symbol}: {str(e)}")
            return None


@task
def check_symbol_status() -> List[str]:
    """Task to check status of all active symbols and deactivate any that are no longer valid."""
    logger.info("Checking symbol status...")
    inactive_symbols = []
    
    try:
        # Get all active symbols
        active_symbols = SymbolManager.get_active_symbols()
        alpaca_source = AlpacaDataSource()
        
        for symbol in active_symbols:
            try:
                # Try to get latest data for the symbol
                data = alpaca_source.get_latest_data(symbol)
                if data is None or data.empty:
                    logger.warning(f"No data available for symbol {symbol}, marking as inactive")
                    if SymbolManager.deactivate_symbol(symbol):
                        inactive_symbols.append(symbol)
            except Exception as e:
                logger.error(f"Error checking symbol {symbol}: {str(e)}")
                if SymbolManager.deactivate_symbol(symbol):
                    inactive_symbols.append(symbol)
                    
        logger.info(f"Symbol status check completed. Deactivated symbols: {inactive_symbols}")
        return inactive_symbols
        
    except Exception as e:
        logger.error(f"Error in symbol status check: {str(e)}")
        raise


@task
def cleanup_old_data(days_to_keep: int = 3):
    """Task to clean up old market data and logs."""
    logger.info(f"Cleaning up data older than {days_to_keep} days...")
    
    try:
        db = DatabaseManager()
        with db.get_session() as session:
            # Delete old market data
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            stmt = text("""
                DELETE FROM market_data 
                WHERE timestamp < :cutoff_date
            """)
            result = session.execute(stmt, {'cutoff_date': cutoff_date})
            deleted_rows = result.rowcount
            
            # Delete old logs
            stmt = text("""
                DELETE FROM logs 
                WHERE timestamp < :cutoff_date
            """)
            result = session.execute(stmt, {'cutoff_date': cutoff_date})
            deleted_logs = result.rowcount
            
            session.commit()
            
        logger.info(f"Cleanup completed. Deleted {deleted_rows} market data rows and {deleted_logs} log entries")
        
    except Exception as e:
        logger.error(f"Error in data cleanup: {str(e)}")
        raise


@task
def send_maintenance_report(inactive_symbols: List[str], deleted_data_count: int, deleted_logs_count: int):
    """Task to log maintenance report."""
    try:
        # Get system info
        system_info = {
            "hostname": platform.node(),
            "python_version": f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "architecture": platform.architecture()[0],
            "platform": platform.platform(),
        }
        
        # Log maintenance results
        logger.info("=== End-of-Day Maintenance Report ===")
        logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        logger.info("System Information:")
        for key, value in system_info.items():
            logger.info(f"  {key}: {value}")
        
        logger.info("Maintenance Results:")
        logger.info(f"  Deactivated Symbols: {', '.join(inactive_symbols) if inactive_symbols else 'None'}")
        logger.info(f"  Deleted Market Data Rows: {deleted_data_count}")
        logger.info(f"  Deleted Log Entries: {deleted_logs_count}")
        logger.info("===================================")
        
    except Exception as e:
        logger.error(f"Error generating maintenance report: {str(e)}")
        raise


@flow(name="End-of-Day Maintenance", 
      flow_run_name=generate_flow_run_name("eod-maintenance"),
      task_runner=DaskTaskRunner(cluster_kwargs={"n_workers": 3, "processes": False}))
def end_of_day_maintenance_flow():
    """Flow for end-of-day maintenance tasks."""
    logger.info("Starting end-of-day maintenance flow...")
    
    # Check symbol status
    inactive_symbols = check_symbol_status()
    
    # Clean up old data
    cleanup_old_data()
    
    # Send maintenance report
    send_maintenance_report(inactive_symbols, deleted_data_count=0, deleted_logs_count=0)
    
    logger.info("End-of-day maintenance flow completed successfully")
