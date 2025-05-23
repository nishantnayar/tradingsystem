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
        interval: str = "1h"
    ) -> pd.DataFrame:
        """Get the latest data from Alpaca."""
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=100)  # Get last 24 hours
        return self.get_historical_data(symbol, start_date, end_date, interval)

    def get_multiple_symbols(
        self,
        symbols: List[str],
        interval: str = "1h"
    ) -> Dict[str, pd.DataFrame]:
        """Get data for multiple symbols from Alpaca."""
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=1)
        
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
            
        # Log the actual columns we receive
        logger.debug(f"Standardizing columns. Available columns: {df.columns.tolist()}")
        
        # Map Alpaca's abbreviated column names to our expected format
        column_map = {
            "o": "open",
            "h": "high",
            "l": "low",
            "c": "close",
            "v": "volume",
            "n": "trade_count",
            "vw": "vwap",
            "t": "timestamp"
        }
        
        # Create a new DataFrame with only the columns we need
        standardized_df = pd.DataFrame()
        for alpaca_col, our_col in column_map.items():
            if alpaca_col in df.columns:
                standardized_df[our_col] = df[alpaca_col]
            else:
                logger.warning(f"Column {alpaca_col} not found in DataFrame")
        
        # Convert timestamp to datetime if it exists
        if 'timestamp' in standardized_df.columns:
            try:
                # First try parsing as ISO format
                standardized_df['timestamp'] = pd.to_datetime(standardized_df['timestamp'])
            except (ValueError, TypeError):
                try:
                    # If that fails, try parsing as Unix timestamp (milliseconds)
                    standardized_df['timestamp'] = pd.to_datetime(standardized_df['timestamp'], unit='ms')
                except (ValueError, TypeError) as e:
                    logger.error(f"Failed to convert timestamp: {e}")
                    # If both fail, return empty DataFrame
                    return pd.DataFrame()
            
            logger.debug(f"Converted timestamp column to datetime. Sample: {standardized_df['timestamp'].iloc[0]}")
        
        logger.debug(f"Standardized columns: {standardized_df.columns.tolist()}")
        return standardized_df 