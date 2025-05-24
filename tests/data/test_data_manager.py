import pytest
from datetime import datetime, timedelta
import pandas as pd
from unittest.mock import Mock, patch

from src.data.data_manager import DataManager
from src.data.symbol_manager import SymbolManager


@pytest.fixture
def mock_alpaca_source():
    """Create a mock Alpaca data source."""
    with patch('src.data.data_manager.AlpacaDataSource') as mock:
        yield mock


@pytest.fixture
def sample_data():
    """Create sample market data."""
    dates = pd.date_range(start='2024-01-01', periods=5, freq='H')
    return pd.DataFrame({
        'open': [100.0, 101.0, 102.0, 103.0, 104.0],
        'high': [101.0, 102.0, 103.0, 104.0, 105.0],
        'low': [99.0, 100.0, 101.0, 102.0, 103.0],
        'close': [100.5, 101.5, 102.5, 103.5, 104.5],
        'volume': [1000, 1100, 1200, 1300, 1400]
    }, index=dates)


def test_get_latest_data_success(mock_alpaca_source, sample_data):
    """Test successful data retrieval."""
    # Setup
    symbol = "AAPL"
    mock_alpaca_source.return_value.get_latest_data.return_value = sample_data
    
    # Execute
    data_manager = DataManager()
    result = data_manager.get_latest_data(symbol)
    
    # Assert
    assert result is not None
    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert all(col in result.columns for col in ['open', 'high', 'low', 'close', 'volume'])
    mock_alpaca_source.return_value.get_latest_data.assert_called_once_with(symbol)


def test_get_latest_data_no_data(mock_alpaca_source):
    """Test data retrieval when no data is available."""
    # Setup
    symbol = "INVALID"
    mock_alpaca_source.return_value.get_latest_data.return_value = None
    
    # Execute
    data_manager = DataManager()
    result = data_manager.get_latest_data(symbol)
    
    # Assert
    assert result is None


def test_get_latest_data_empty_dataframe(mock_alpaca_source):
    """Test data retrieval when empty DataFrame is returned."""
    # Setup
    symbol = "AAPL"
    mock_alpaca_source.return_value.get_latest_data.return_value = pd.DataFrame()
    
    # Execute
    data_manager = DataManager()
    result = data_manager.get_latest_data(symbol)
    
    # Assert
    assert result is None


def test_market_data_collection_flow(mock_alpaca_source, sample_data):
    """Test the market data collection flow."""
    # Setup
    mock_alpaca_source.return_value.get_multiple_symbols.return_value = {
        "AAPL": sample_data,
        "GOOGL": sample_data
    }
    
    # Execute
    from src.data.data_manager import market_data_collection_flow
    result = market_data_collection_flow()
    
    # Assert
    assert result is not None
    mock_alpaca_source.return_value.get_multiple_symbols.assert_called_once() 