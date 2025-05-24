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
        lookback_days: int = 1  # Default to 1 year of data
    ) -> pd.DataFrame:
        """Get the latest data from Alpaca.
        
        Args:
            symbol: The stock symbol
            interval: Data interval (e.g., "1h", "1d")
            lookback_days: Number of days of historical data to fetch (default: 365)
        """
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=lookback_days)
        return self.get_historical_data(symbol, start_date, end_date, interval)

    def get_multiple_symbols(
        self,
        symbols: List[str],
        interval: str = "1h",
        lookback_days: int = 1  # Default to 1 year of data
    ) -> Dict[str, pd.DataFrame]:
        """Get data for multiple symbols from Alpaca.
        
        Args:
            symbols: List of stock symbols
            interval: Data interval (e.g., "1h", "1d")
            lookback_days: Number of days of historical data to fetch (default: 365)
        """
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=lookback_days)
        
        request_params = StockBarsRequest(
            symbol_or_symbols=symbols,
            timeframe=self._convert_interval(interval),
            start=start_date,
            end=end_date,
            feed="iex"  # Use IEX feed instead of SIP
        )
        
        try:
            bars = self.client.get_stock_bars(request_params)
            # Convert the response to a dictionary of DataFrames
            result = {}
            for symbol in symbols:
                if symbol in bars:
                    df = pd.DataFrame(bars[symbol])
                    
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
            return df
            
        # Create a list to store the standardized data
        standardized_data = []
        
        # Get the symbol column if it exists
        symbol_column = None
        for col in df.columns:
            if col != 'symbol' and col != 'timestamp' and col != 'index':
                symbol_column = col
                break
        
        if symbol_column is None:
            logger.error("No symbol data column found in DataFrame")
            return pd.DataFrame()
            
        # Extract data from each row
        for idx, row in df.iterrows():
            if isinstance(row[symbol_column], dict):
                data_point = {
                    'open': row[symbol_column].get('o', 0),
                    'high': row[symbol_column].get('h', 0),
                    'low': row[symbol_column].get('l', 0),
                    'close': row[symbol_column].get('c', 0),
                    'volume': row[symbol_column].get('v', 0),
                    'trade_count': row[symbol_column].get('n', 0),
                    'vwap': row[symbol_column].get('vw', 0),
                    'timestamp': row[symbol_column].get('t', 0),
                    'symbol': row['symbol'] if 'symbol' in row else symbol_column
                }
                standardized_data.append(data_point)
        
        # Create DataFrame from the standardized data
        standardized_df = pd.DataFrame(standardized_data)
        
        # Set timestamp as index if it exists
        if 'timestamp' in standardized_df.columns:
            try:
                # Convert timestamp to datetime
                standardized_df['timestamp'] = pd.to_datetime(standardized_df['timestamp'])
                # Set as index
                standardized_df.set_index('timestamp', inplace=True)
            except (ValueError, TypeError) as e:
                logger.error(f"Failed to convert timestamp: {e}")
                return pd.DataFrame()
        
        # Add missing columns with default values
        required_columns = ['open', 'high', 'low', 'close', 'volume', 'trade_count', 'vwap']
        for col in required_columns:
            if col not in standardized_df.columns:
                standardized_df[col] = 0
        
        return standardized_df 