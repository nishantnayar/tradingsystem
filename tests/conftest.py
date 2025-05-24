import pytest
from datetime import datetime, timedelta
import pandas as pd
from unittest.mock import Mock, patch

from src.database.models import Symbol, MarketData


@pytest.fixture
def sample_market_data():
    """Create sample market data."""
    dates = pd.date_range(start='2024-01-01', periods=5, freq='H')
    return pd.DataFrame({
        'open': [100.0, 101.0, 102.0, 103.0, 104.0],
        'high': [101.0, 102.0, 103.0, 104.0, 105.0],
        'low': [99.0, 100.0, 101.0, 102.0, 103.0],
        'close': [100.5, 101.5, 102.5, 103.5, 104.5],
        'volume': [1000, 1100, 1200, 1300, 1400]
    }, index=dates)


@pytest.fixture
def sample_symbol():
    """Create a sample symbol."""
    return Symbol(
        symbol="AAPL",
        name="Apple Inc.",
        is_active=True,
        start_date=datetime.utcnow()
    )


@pytest.fixture
def sample_market_data_record():
    """Create a sample market data record."""
    return MarketData(
        symbol="AAPL",
        timestamp=datetime.utcnow(),
        open=100.0,
        high=101.0,
        low=99.0,
        close=100.5,
        volume=1000
    )


@pytest.fixture
def mock_db_manager():
    """Create a mock database manager."""
    with patch('src.database.db_manager.DatabaseManager') as mock:
        yield mock


@pytest.fixture
def mock_alpaca_client():
    """Create a mock Alpaca client."""
    with patch('src.data.sources.alpaca_source.StockHistoricalDataClient') as mock:
        yield mock


@pytest.fixture
def mock_prefect_client():
    """Create a mock Prefect client."""
    with patch('prefect.client.Client') as mock:
        yield mock 