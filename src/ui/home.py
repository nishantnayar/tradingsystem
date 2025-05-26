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
from src.ui.components.data_display import display_market_data, format_refresh_time
from src.ui.components.chart_display import display_chart, display_chart_simplified
from src.database.db_manager import DatabaseManager
from src.ui.state.market_data_state import (
    get_market_data,
    get_latest_price,
    get_price_change,
    get_last_refresh_time
)


def render_home():
    """Render the home page of the trading system."""
    st.title("Trading System Dashboard")
    
    # Display market status at the top
    display_market_status()
    
    # Add a separator
    st.markdown("---")
    
    # Controls section
    st.subheader("Controls")
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Add refresh button
        if st.button("🔄 Refresh Data"):
            st.session_state.force_refresh = True
            
        # Display last refresh time if a symbol is selected
        if 'selected_symbol' in st.session_state:
            last_refresh = get_last_refresh_time(st.session_state.selected_symbol)
            if last_refresh:
                st.write(f"Last updated: {format_refresh_time(last_refresh)}")
    
    with col2:
        st.subheader("Symbol Selection")
        selected_symbol = display_symbol_selector()
        if selected_symbol:
            st.session_state.selected_symbol = selected_symbol
    
    # Add a separator
    st.markdown("---")
    
    if selected_symbol:
        # Display market data
        st.subheader(f"Market Data for {selected_symbol}")
        display_market_data(
            selected_symbol,
            force_refresh=st.session_state.get('force_refresh', False)
        )

        # Display chart with default indicators
        st.subheader("Price Chart")
        display_chart_simplified(
            selected_symbol,
            #indicators={'sma': {'period': 20}},
            force_refresh=st.session_state.get('force_refresh', False)
        )

        # Reset force refresh flag
        if 'force_refresh' in st.session_state:
            st.session_state.force_refresh = False
    else:
        st.info("Please select a symbol to view market data")


def is_market_open() -> bool:
    """Check if the market is currently open."""
    now = datetime.now()
    # Simple check for market hours (9:30 AM - 4:00 PM ET)
    market_open = now.replace(hour=9, minute=30, second=0)
    market_close = now.replace(hour=16, minute=0, second=0)
    return market_open <= now <= market_close 