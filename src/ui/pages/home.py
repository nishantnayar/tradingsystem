"""
Home page for the trading system dashboard.
"""
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from loguru import logger
from sqlalchemy import text

from src.data.data_manager import DataManager
from src.data.symbol_manager import SymbolManager
from src.ui.components.market_status import display_market_status
from src.ui.components.symbol_selector import display_symbol_selector
from src.ui.components.data_display import display_market_data
from src.ui.components.chart_display import display_chart
from src.database.db_manager import DatabaseManager


def render_home():
    """Render the home page of the trading system."""
    st.title("Trading System Dashboard")
    
    # Display market status at the top
    display_market_status()
    
    # Add a separator
    st.markdown("---")
    
    # Create two columns for symbol selection and data display
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Symbol Selection")
    with col2:
        selected_symbol = display_symbol_selector()

    if selected_symbol:
        # Display market data
        st.subheader(f"Market Data for {selected_symbol}")
        display_market_data(selected_symbol)

        # Display chart with default indicators
        st.subheader("Price Chart")
        display_chart(
            selected_symbol,
            indicators={'sma': {'period': 20}}
        )
    else:
        st.info("Please select a symbol to view market data")


def is_market_open() -> bool:
    """Check if the market is currently open."""
    now = datetime.now()
    # Simple check for market hours (9:30 AM - 4:00 PM ET)
    market_open = now.replace(hour=9, minute=30, second=0)
    market_close = now.replace(hour=16, minute=0, second=0)
    return market_open <= now <= market_close 