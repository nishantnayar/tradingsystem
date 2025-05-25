import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from loguru import logger
import pandas as pd
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy import text

from src.database.db_manager import DatabaseManager


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


def display_chart(symbol: str, indicators: Optional[Dict[str, Any]] = None):
    """Display price chart for a symbol.
    
    Args:
        symbol: The stock symbol to display chart for
        indicators: Optional dictionary of indicators to add to the chart
    """
    try:
        # Get database connection
        db = DatabaseManager()

        # Query the latest data from the database
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

            if data.empty:
                st.warning(f"No data available for {symbol}")
                return

            # Create and display the chart
            fig = create_candlestick_chart(data, symbol, indicators)
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        logger.error(f"Error displaying chart for {symbol}: {e}")
        st.error("Error loading chart. Please try again later.") 