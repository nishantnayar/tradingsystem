"""
Home page for the trading system dashboard.
"""
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.data.data_manager import DataManager
from src.data.symbol_manager import SymbolManager


def render_home():
    """Render the home page with market overview."""
    st.title("Trading System Dashboard")
    
    # Sidebar filters
    with st.sidebar:
        st.header("Filters")
        
        # Date range selector
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        date_range = st.date_input(
            "Date Range",
            value=(start_date, end_date),
            max_value=end_date
        )
        
        # Symbol selector
        symbols = SymbolManager.get_active_symbols()
        selected_symbols = st.multiselect(
            "Select Symbols",
            options=symbols,
            default=symbols[:5] if symbols else []
        )
    
    # Main content area with tabs
    tab1, tab2, tab3 = st.tabs(["Market Overview", "Portfolio", "Analysis"])
    
    with tab1:
        st.header("Market Overview")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Active Symbols")
            st.write(f"Total Active Symbols: {len(symbols)}")
            
            # Display symbol list
            if symbols:
                symbol_df = pd.DataFrame({
                    'Symbol': symbols,
                    'Status': ['Active'] * len(symbols)
                })
                st.dataframe(symbol_df, use_container_width=True)
        
        with col2:
            st.subheader("Market Status")
            st.metric("Market Hours", "Open" if is_market_open() else "Closed")
            st.metric("Last Update", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    with tab2:
        st.header("Portfolio Overview")
        # Placeholder for portfolio metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Value", "$100,000", "+2.5%")
        with col2:
            st.metric("Daily P&L", "$2,500", "+2.5%")
        with col3:
            st.metric("Open Positions", "5", "0")
    
    with tab3:
        st.header("Market Analysis")
        if selected_symbols:
            # Create a sample price chart
            fig = create_price_chart(selected_symbols[0])
            st.plotly_chart(fig, use_container_width=True)


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