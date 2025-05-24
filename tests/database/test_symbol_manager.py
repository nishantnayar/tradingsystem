import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from src.data.symbol_manager import SymbolManager
from src.database.models import Symbol


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    with patch('src.data.symbol_manager.DatabaseManager') as mock:
        session = Mock()
        mock.return_value.get_session.return_value.__enter__.return_value = session
        yield session


def test_add_symbol_new(mock_db_session):
    """Test adding a new symbol."""
    # Setup
    symbol = "AAPL"
    name = "Apple Inc."
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = None
    
    # Execute
    result = SymbolManager.add_symbol(symbol, name)
    
    # Assert
    assert isinstance(result, Symbol)
    assert result.symbol == symbol
    assert result.name == name
    assert result.is_active
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()


def test_add_symbol_existing_active(mock_db_session):
    """Test adding an existing active symbol."""
    # Setup
    symbol = "AAPL"
    existing_symbol = Symbol(symbol=symbol, is_active=True)
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = existing_symbol
    
    # Execute
    result = SymbolManager.add_symbol(symbol)
    
    # Assert
    assert result == existing_symbol
    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_not_called()


def test_add_symbol_existing_inactive(mock_db_session):
    """Test reactivating an existing inactive symbol."""
    # Setup
    symbol = "AAPL"
    existing_symbol = Symbol(symbol=symbol, is_active=False)
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = existing_symbol
    
    # Execute
    result = SymbolManager.add_symbol(symbol)
    
    # Assert
    assert result == existing_symbol
    assert result.is_active
    assert result.end_date is None
    mock_db_session.commit.assert_called_once()


def test_deactivate_symbol(mock_db_session):
    """Test deactivating a symbol."""
    # Setup
    symbol = "AAPL"
    existing_symbol = Symbol(symbol=symbol, is_active=True)
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = existing_symbol
    
    # Execute
    result = SymbolManager.deactivate_symbol(symbol)
    
    # Assert
    assert result is True
    assert not existing_symbol.is_active
    assert existing_symbol.end_date is not None
    mock_db_session.commit.assert_called_once()


def test_get_active_symbols(mock_db_session):
    """Test getting active symbols."""
    # Setup
    symbols = [
        Symbol(symbol="AAPL", is_active=True),
        Symbol(symbol="GOOGL", is_active=True),
        Symbol(symbol="MSFT", is_active=False)
    ]
    mock_db_session.query.return_value.filter_by.return_value.all.return_value = symbols[:2]
    
    # Execute
    result = SymbolManager.get_active_symbols()
    
    # Assert
    assert len(result) == 2
    assert "AAPL" in result
    assert "GOOGL" in result
    assert "MSFT" not in result


def test_get_symbol_info(mock_db_session):
    """Test getting symbol information."""
    # Setup
    symbol = "AAPL"
    existing_symbol = Symbol(
        symbol=symbol,
        name="Apple Inc.",
        is_active=True,
        start_date=datetime.utcnow()
    )
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = existing_symbol
    
    # Execute
    result = SymbolManager.get_symbol_info(symbol)
    
    # Assert
    assert isinstance(result, Symbol)
    assert result.symbol == symbol
    assert result.name == "Apple Inc."
    assert result.is_active


def test_update_symbol_name(mock_db_session):
    """Test updating symbol name."""
    # Setup
    symbol = "AAPL"
    new_name = "Apple Inc. (New)"
    existing_symbol = Symbol(symbol=symbol, name="Apple Inc.")
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = existing_symbol
    
    # Execute
    result = SymbolManager.update_symbol_name(symbol, new_name)
    
    # Assert
    assert result is True
    assert existing_symbol.name == new_name
    mock_db_session.commit.assert_called_once() 