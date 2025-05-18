from datetime import datetime, timedelta
from typing import Dict, List

import pandas as pd
import yfinance as yf

from src.data.sources.base import DataSource


class YahooDataSource(DataSource):
    """Yahoo Finance data source implementation."""

    def get_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1h"
    ) -> pd.DataFrame:
        """Get historical data from Yahoo Finance."""
        ticker = yf.Ticker(symbol)
        df = ticker.history(
            start=start_date,
            end=end_date,
            interval=interval
        )
        return self._standardize_columns(df)

    def get_latest_data(
        self,
        symbol: str,
        interval: str = "1h"
    ) -> pd.DataFrame:
        """Get the latest data from Yahoo Finance."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)
        return self.get_historical_data(symbol, start_date, end_date, interval)

    def get_multiple_symbols(
        self,
        symbols: List[str],
        interval: str = "1h"
    ) -> Dict[str, pd.DataFrame]:
        """Get data for multiple symbols from Yahoo Finance."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)
        
        result = {}
        for symbol in symbols:
            result[symbol] = self.get_historical_data(
                symbol, start_date, end_date, interval
            )
        return result

    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names to match Alpaca format."""
        column_map = {
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume"
        }
        return df.rename(columns=column_map) 