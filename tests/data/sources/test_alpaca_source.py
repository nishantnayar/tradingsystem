import pytest
from datetime import datetime, timedelta
import pandas as pd
from unittest.mock import Mock, patch

from src.data.sources.alpaca_source import AlpacaDataSource


@pytest.fixture
def mock_alpaca_client():
    """Create a mock Alpaca client."""
    with patch('src.data.sources.alpaca_source.StockHistoricalDataClient') as mock:
        yield mock


@pytest.fixture
def sample_alpaca_response():
    """Create sample Alpaca API response."""
    return {
        'AAPL': [
            {
                'o': 100.0,
                'h': 101.0,
                'l': 99.0,
                'c': 100.5,
                'v': 1000,
                'n': 500,
                'vw': 100.2,
                't': '2024-01-01T00:00:00Z'
            }
        ]
    }


def test_get_historical_data(mock_alpaca_client, sample_alpaca_response):
    """Test historical data retrieval."""
    # Setup
    symbol = "AAPL"
    start_date = datetime.now() - timedelta(days=1)
    end_date = datetime.now()
    mock_alpaca_client.return_value.get_stock_bars.return_value = sample_alpaca_response
    
    # Execute
    source = AlpacaDataSource()
    result = source.get_historical_data(symbol, start_date, end_date)
    
    # Assert
    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert all(col in result.columns for col in ['open', 'high', 'low', 'close', 'volume'])
    mock_alpaca_client.return_value.get_stock_bars.assert_called_once()


def test_get_latest_data(mock_alpaca_client, sample_alpaca_response):
    """Test latest data retrieval."""
    # Setup
    symbol = "AAPL"
    mock_alpaca_client.return_value.get_stock_bars.return_value = sample_alpaca_response
    
    # Execute
    source = AlpacaDataSource()
    result = source.get_latest_data(symbol)
    
    # Assert
    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert all(col in result.columns for col in ['open', 'high', 'low', 'close', 'volume'])


def test_get_multiple_symbols(mock_alpaca_client, sample_alpaca_response):
    """Test multiple symbols data retrieval."""
    # Setup
    symbols = ["AAPL", "GOOGL"]
    mock_alpaca_client.return_value.get_stock_bars.return_value = sample_alpaca_response
    
    # Execute
    source = AlpacaDataSource()
    result = source.get_multiple_symbols(symbols)
    
    # Assert
    assert isinstance(result, dict)
    assert all(symbol in result for symbol in symbols)
    assert all(isinstance(df, pd.DataFrame) for df in result.values())


def test_standardize_columns():
    """Test column standardization."""
    # Setup
    source = AlpacaDataSource()
    df = pd.DataFrame({
        'AAPL': [{
            'o': 100.0,
            'h': 101.0,
            'l': 99.0,
            'c': 100.5,
            'v': 1000,
            'n': 500,
            'vw': 100.2,
            't': '2024-01-01T00:00:00Z'
        }],
        'symbol': ['AAPL']
    })
    
    # Execute
    result = source._standardize_columns(df)
    
    # Assert
    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert all(col in result.columns for col in ['open', 'high', 'low', 'close', 'volume'])
    assert isinstance(result.index, pd.DatetimeIndex)


def test_convert_interval():
    """Test interval conversion."""
    # Setup
    source = AlpacaDataSource()
    
    # Execute and Assert
    assert source._convert_interval("1m") == "Minute"
    assert source._convert_interval("1h") == "Hour"
    assert source._convert_interval("1d") == "Day"
    assert source._convert_interval("invalid") == "Hour"  # Default case 