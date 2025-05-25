"""
Home page for the trading system dashboard.
"""
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from loguru import logger

from src.data.data_manager import DataManager
from src.data.symbol_manager import SymbolManager
from src.ui.components.market_status import display_market_status
from src.ui.components.symbol_selector import display_symbol_selector
from src.ui.components.data_display import display_market_data
from src.ui.components.chart_display import display_chart


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
        selected_symbol = display_symbol_selector()
    
    with col2:
        if selected_symbol:
            st.subheader(f"Market Data for {selected_symbol}")
            display_market_data(selected_symbol)
            
            # Display chart below the data
            st.subheader("Price Chart")
            display_chart(selected_symbol)
        else:
            st.info("Please select a symbol to view market data")


def is_market_open() -> bool:
    """Check if the market is currently open."""
    now = datetime.now()
    # Simple check for market hours (9:30 AM - 4:00 PM ET)
    market_open = now.replace(hour=9, minute=30, second=0)
    market_close = now.replace(hour=16, minute=0, second=0)
    return market_open <= now <= market_close


def create_price_chart(symbol: str) -> go.Figure:
    """Create a price chart for the given symbol."""
    # Get data for the symbol
    data_manager = DataManager()
    data = data_manager.get_latest_data(symbol)
    
    if data is None or data.empty:
        return go.Figure()
    
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data['open'],
            high=data['high'],
            low=data['low'],
            close=data['close'],
            name="Price"
        ),
        secondary_y=False
    )
    
    # Add volume bars
    fig.add_trace(
        go.Bar(
            x=data.index,
            y=data['volume'],
            name="Volume"
        ),
        secondary_y=True
    )
    
    # Update layout
    fig.update_layout(
        title=f"{symbol} Price Chart",
        xaxis_title="Date",
        yaxis_title="Price",
        height=600
    )
    
    return fig 