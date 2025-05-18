from datetime import datetime, timedelta
from typing import Dict, List

import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
import sys
from pathlib import Path

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
            end=end_date
        )
        
        bars = self.client.get_stock_bars(request_params)
        return pd.DataFrame(bars)

    def get_latest_data(
        self,
        symbol: str,
        interval: str = "1h"
    ) -> pd.DataFrame:
        """Get the latest data from Alpaca."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)  # Get last 24 hours
        return self.get_historical_data(symbol, start_date, end_date, interval)

    def get_multiple_symbols(
        self,
        symbols: List[str],
        interval: str = "1h"
    ) -> Dict[str, pd.DataFrame]:
        """Get data for multiple symbols from Alpaca."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)
        
        request_params = StockBarsRequest(
            symbol_or_symbols=symbols,
            timeframe=self._convert_interval(interval),
            start=start_date,
            end=end_date
        )
        
        bars = self.client.get_stock_bars(request_params)
        # Convert the response to a dictionary of DataFrames
        result = {}
        for symbol in symbols:
            if symbol in bars:
                result[symbol] = pd.DataFrame(bars[symbol])
        return result

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