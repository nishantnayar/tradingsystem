from datetime import datetime, timedelta, timezone
from typing import Dict, List

import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
import sys
from pathlib import Path
from loguru import logger

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from src.data.sources.base import DataSource
from src.utils.config import get_config
from src.utils.market_hours import MarketHoursManager


class AlpacaDataSource(DataSource):
    """Alpaca data source implementation."""

    def __init__(self):
        config = get_config()
        alpaca_config = config["alpaca"]
        self.client = StockHistoricalDataClient(
            api_key=alpaca_config["api_key"],
            secret_key=alpaca_config["secret_key"],
            raw_data=True  # Get raw data for better performance
        )
        self.market_hours = MarketHoursManager()

    def get_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1h"
    ) -> pd.DataFrame:
        """Get historical data from Alpaca."""
        timeframe = self._convert_interval(interval)
        
        request_params = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=timeframe,
            start=start_date,
            end=end_date,
            feed="iex"  # Use IEX feed instead of SIP
        )
        
        try:
            bars = self.client.get_stock_bars(request_params)
            df = pd.DataFrame(bars)
            
            # Add symbol column and reset index
            df.insert(0, "symbol", symbol)
            df.reset_index(inplace=True)
            
            # Add missing columns if not present
            if 'trade_count' not in df.columns:
                df['trade_count'] = 0
            if 'vwap' not in df.columns:
                df['vwap'] = 0
                
            return self._standardize_columns(df)
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return pd.DataFrame()  # Return empty DataFrame on error

    def get_latest_data(
        self,
        symbol: str,
        interval: str = "1h",
        lookback_days: int = 10  # Default to 1 day of data
    ) -> pd.DataFrame:
        """Get the latest data from Alpaca.
        
        Args:
            symbol: The stock symbol
            interval: Data interval (e.g., "1h", "1d")
            lookback_days: Number of days of historical data to fetch (default: 1)
        """
        end_date = datetime.now(timezone.utc)
        
        # If market is closed, adjust end_date to last market close
        if not self.market_hours.is_market_open():
            market_hours = self.market_hours.get_market_hours(end_date)
            if market_hours:
                end_date = market_hours["close"]
            else:
                # If we can't get market hours, use previous day's close
                end_date = end_date - timedelta(days=1)
                end_date = end_date.replace(hour=16, minute=0, second=0, microsecond=0)
        
        start_date = end_date - timedelta(days=lookback_days)
        return self.get_historical_data(symbol, start_date, end_date, interval)

    def get_multiple_symbols(
        self,
        symbols: List[str],
        interval: str = "1h",
        lookback_days: int = 10  # Default to 1 day of data
    ) -> Dict[str, pd.DataFrame]:
        """Get data for multiple symbols from Alpaca."""
        logger.debug(f"Getting data for symbols: {symbols}")
        end_date = datetime.now(timezone.utc)
        
        # If market is closed, adjust end_date to last market close
        if not self.market_hours.is_market_open():
            market_hours = self.market_hours.get_market_hours(end_date)
            if market_hours:
                end_date = market_hours["close"]
            else:
                # If we can't get market hours, use previous day's close
                end_date = end_date - timedelta(days=1)
                end_date = end_date.replace(hour=16, minute=0, second=0, microsecond=0)
        
        start_date = end_date - timedelta(days=lookback_days)
        logger.debug(f"Date range: {start_date} to {end_date}")
        
        request_params = StockBarsRequest(
            symbol_or_symbols=symbols,
            timeframe=self._convert_interval(interval),
            start=start_date,
            end=end_date,
            feed="iex"  # Use IEX feed instead of SIP
        )
        
        try:
            logger.debug("Making API request to Alpaca...")
            bars = self.client.get_stock_bars(request_params)
            logger.debug(f"Received response from Alpaca for {len(symbols)} symbols")
            
            # Convert the response to a dictionary of DataFrames
            result = {}
            for symbol in symbols:
                if symbol in bars:
                    df = pd.DataFrame(bars[symbol])
                    logger.debug(f"Got data for {symbol}: {len(df)} rows")
                    
                    # Add symbol column and reset index
                    df.insert(0, "symbol", symbol)
                    df.reset_index(inplace=True)
                    
                    # Add missing columns if not present
                    if 'trade_count' not in df.columns:
                        df['trade_count'] = 0
                    if 'vwap' not in df.columns:
                        df['vwap'] = 0
                        
                    result[symbol] = self._standardize_columns(df)
                else:
                    logger.warning(f"No data available for symbol {symbol}")
            return result
        except Exception as e:
            logger.error(f"Error fetching data for multiple symbols: {str(e)}")
            return {}

    def get_extended_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d"  # Default to daily data for longer periods
    ) -> pd.DataFrame:
        """Get extended historical data from Alpaca.
        
        This method is designed for fetching large amounts of historical data
        for training purposes. It handles pagination and rate limits automatically.
        
        Args:
            symbol: The stock symbol
            start_date: Start date for historical data
            end_date: End date for historical data
            interval: Data interval (e.g., "1h", "1d")
            
        Returns:
            DataFrame containing the historical data
        """
        try:
            # For extended historical data, use daily bars by default
            timeframe = self._convert_interval(interval)
            
            # Calculate the number of days between start and end
            days_diff = (end_date - start_date).days
            
            # If requesting more than 1 year of data, use daily bars
            if days_diff > 365 and interval == "1h":
                logger.warning("Requesting more than 1 year of hourly data. Switching to daily bars.")
                timeframe = TimeFrame.Day
            
            request_params = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=timeframe,
                start=start_date,
                end=end_date,
                feed="iex"
            )
            
            bars = self.client.get_stock_bars(request_params)
            df = pd.DataFrame(bars)
            
            # Add symbol column and reset index
            df.insert(0, "symbol", symbol)
            df.reset_index(inplace=True)
            
            # Add missing columns if not present
            if 'trade_count' not in df.columns:
                df['trade_count'] = 0
            if 'vwap' not in df.columns:
                df['vwap'] = 0
                
            return self._standardize_columns(df)
            
        except Exception as e:
            logger.error(f"Error fetching extended historical data for {symbol}: {str(e)}")
            return pd.DataFrame()  # Return empty DataFrame on error

    def _convert_interval(self, interval: str) -> TimeFrame:
        """Convert string interval to Alpaca TimeFrame."""
        interval_map = {
            "1m": TimeFrame.Minute,
            "5m": TimeFrame.Minute,
            "15m": TimeFrame.Minute,
            "30m": TimeFrame.Minute,
            "1h": TimeFrame.Hour,
            "1d": TimeFrame.Day,
        }
        return interval_map.get(interval, TimeFrame.Hour)

    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names to match our expected format."""
        if df.empty:
            logger.debug("Empty DataFrame received in _standardize_columns")
            return df
            
        logger.debug(f"Input DataFrame columns: {df.columns.tolist()}")
        logger.debug(f"Input DataFrame head:\n{df.head()}")
            
        # Create a mapping for the single-letter columns
        column_map = {
            'o': 'open',
            'h': 'high',
            'l': 'low',
            'c': 'close',
            'v': 'volume',
            'n': 'trade_count',
            'vw': 'vwap',
            't': 'timestamp'
        }
        
        # Create a new DataFrame with standardized column names
        standardized_df = df.copy()
        
        # Rename columns if they exist
        for old_col, new_col in column_map.items():
            if old_col in standardized_df.columns:
                standardized_df[new_col] = standardized_df[old_col]
                logger.debug(f"Renamed column {old_col} to {new_col}")
        
        # Ensure all required columns exist
        required_columns = ['open', 'high', 'low', 'close', 'volume', 'trade_count', 'vwap']
        for col in required_columns:
            if col not in standardized_df.columns:
                standardized_df[col] = 0
                logger.debug(f"Added missing column: {col}")
        
        # Set timestamp as index if it exists
        if 'timestamp' in standardized_df.columns:
            try:
                # Convert timestamp to datetime
                standardized_df['timestamp'] = pd.to_datetime(standardized_df['timestamp'])
                # Set as index
                standardized_df.set_index('timestamp', inplace=True)
                logger.debug("Successfully set timestamp as index")
            except (ValueError, TypeError) as e:
                logger.error(f"Failed to convert timestamp: {e}")
                logger.debug(f"Timestamp column data: {standardized_df['timestamp'].head()}")
                return pd.DataFrame()
        
        # Keep only the required columns
        standardized_df = standardized_df[required_columns]
        
        logger.debug(f"Final DataFrame shape: {standardized_df.shape}")
        logger.debug(f"Final DataFrame columns: {standardized_df.columns.tolist()}")
        return standardized_df 