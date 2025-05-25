"""
State management for market data to minimize database hits.
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from loguru import logger
from sqlalchemy import text
from typing import Optional, Dict, Any

from src.database.db_manager import DatabaseManager


def get_market_data(symbol: str, force_refresh: bool = False) -> Optional[pd.DataFrame]:
    """Get market data for a symbol, using cached data if available.
    
    Args:
        symbol: The stock symbol to get data for
        force_refresh: Whether to force a refresh of the data
        
    Returns:
        Optional[pd.DataFrame]: The market data or None if not available
    """
    # Initialize session state for market data if not exists
    if 'market_data' not in st.session_state:
        st.session_state.market_data = {}
    
    # Check if we need to refresh the data
    current_time = datetime.now()
    cache_key = f"{symbol}_data"
    cache_time_key = f"{symbol}_last_update"
    
    should_refresh = (
        force_refresh or
        cache_key not in st.session_state.market_data or
        cache_time_key not in st.session_state.market_data or
        (current_time - st.session_state.market_data[cache_time_key]) > timedelta(minutes=5)
    )
    
    if should_refresh:
        try:
            # Get fresh data from database
            db = DatabaseManager()
            with db.get_session() as session:
                query = text("""
                    SELECT timestamp, open, high, low, close, volume
                    FROM market_data
                    WHERE symbol = :symbol
                    AND timestamp > '2025-01-01'
                    ORDER BY timestamp DESC
                """)

                result = session.execute(query, {'symbol': symbol})
                data = pd.DataFrame(
                    result.fetchall(),
                    columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
                )
                
                if not data.empty:
                    # Update cache
                    st.session_state.market_data[cache_key] = data
                    st.session_state.market_data[cache_time_key] = current_time
                    return data
                else:
                    logger.warning(f"No data available for {symbol}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching market data for {symbol}: {e}")
            return None
    
    # Return cached data
    return st.session_state.market_data.get(cache_key)


def get_last_refresh_time(symbol: str) -> Optional[datetime]:
    """Get the last refresh time for a symbol.
    
    Args:
        symbol: The stock symbol to get refresh time for
        
    Returns:
        Optional[datetime]: The last refresh time or None if not available
    """
    if 'market_data' not in st.session_state:
        return None
        
    cache_time_key = f"{symbol}_last_update"
    return st.session_state.market_data.get(cache_time_key)


def clear_market_data_cache(symbol: Optional[str] = None):
    """Clear the market data cache for a specific symbol or all symbols.
    
    Args:
        symbol: The symbol to clear cache for, or None to clear all
    """
    if 'market_data' not in st.session_state:
        return
        
    if symbol:
        # Clear specific symbol cache
        cache_key = f"{symbol}_data"
        cache_time_key = f"{symbol}_last_update"
        st.session_state.market_data.pop(cache_key, None)
        st.session_state.market_data.pop(cache_time_key, None)
    else:
        # Clear all cache
        st.session_state.market_data = {}


def get_latest_price(symbol: str) -> Optional[float]:
    """Get the latest price for a symbol using cached data if available.
    
    Args:
        symbol: The stock symbol to get price for
        
    Returns:
        Optional[float]: The latest price or None if not available
    """
    data = get_market_data(symbol)
    if data is not None and not data.empty:
        return data['close'].iloc[0]
    return None


def get_price_change(symbol: str) -> Optional[float]:
    """Get the 24-hour price change percentage using cached data if available.
    
    Args:
        symbol: The stock symbol to get price change for
        
    Returns:
        Optional[float]: The price change percentage or None if not available
    """
    data = get_market_data(symbol)
    if data is not None and len(data) >= 2:
        return ((data['close'].iloc[0] / data['close'].iloc[1] - 1) * 100)
    return None 