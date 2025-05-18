from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Union

import pandas as pd


class DataSource(ABC):
    """Base class for all data sources."""

    @abstractmethod
    def get_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1h"
    ) -> pd.DataFrame:
        """Get historical data for a symbol."""
        pass

    @abstractmethod
    def get_latest_data(
        self,
        symbol: str,
        interval: str = "1h"
    ) -> pd.DataFrame:
        """Get the latest data for a symbol."""
        pass

    @abstractmethod
    def get_multiple_symbols(
        self,
        symbols: List[str],
        interval: str = "1h"
    ) -> Dict[str, pd.DataFrame]:
        """Get data for multiple symbols."""
        pass 