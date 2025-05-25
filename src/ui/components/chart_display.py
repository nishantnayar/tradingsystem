import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from loguru import logger
import pandas as pd
from typing import Optional, Dict, Any

from src.ui.state.market_data_state import get_market_data


def create_candlestick_chart(
    data: pd.DataFrame,
    symbol: str,
    indicators: Optional[Dict[str, Any]] = None
) -> go.Figure:
    """Create a candlestick chart with optional indicators.
    
    Args:
        data: DataFrame containing OHLCV data
        symbol: The stock symbol
        indicators: Optional dictionary of indicators to add to the chart
        
    Returns:
        go.Figure: The configured Plotly figure
    """
    fig = go.Figure()

    # Add candlestick trace
    fig.add_trace(go.Candlestick(
        x=data.index if isinstance(data.index, pd.DatetimeIndex) else data['timestamp'],
        open=data['open'],
        high=data['high'],
        low=data['low'],
        close=data['close'],
        name=symbol
    ))

    # Add indicators if provided
    if indicators:
        if indicators.get('sma'):
            period = indicators['sma'].get('period', 20)
            fig.add_trace(go.Scatter(
                x=data.index if isinstance(data.index, pd.DatetimeIndex) else data['timestamp'],
                y=data['close'].rolling(window=period).mean(),
                name=f'SMA {period}',
                line=dict(color='blue', width=2)
            ))

    # Update layout
    fig.update_layout(
        title=f'{symbol} Price Chart',
        xaxis_title='Date',
        yaxis_title='Price',
        xaxis_rangeslider_visible=False,
        height=600,
        template='plotly_white'
    )

    return fig


def display_chart(symbol: str, indicators: Optional[Dict[str, Any]] = None, force_refresh: bool = False):
    """Display price chart for a symbol.
    
    Args:
        symbol: The stock symbol to display chart for
        indicators: Optional dictionary of indicators to add to the chart
        force_refresh: Whether to force a refresh of the data
    """
    try:
        # Get data from state management
        data = get_market_data(symbol, force_refresh)
        
        if data is None or data.empty:
            st.warning(f"No data available for {symbol}")
            return

        # Create and display the chart
        fig = create_candlestick_chart(data, symbol, indicators)
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        logger.error(f"Error displaying chart for {symbol}: {e}")
        st.error("Error loading chart. Please try again later.") 