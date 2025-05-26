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
    # Calculate technical indicators
    data = data.copy()
    
    # Calculate moving averages
    data['MA5'] = data['close'].rolling(window=5).mean()
    data['MA20'] = data['close'].rolling(window=20).mean()
    
    # Calculate MACD
    exp1 = data['close'].ewm(span=12, adjust=False).mean()
    exp2 = data['close'].ewm(span=26, adjust=False).mean()
    data['macd'] = exp1 - exp2
    data['macd_signal'] = data['macd'].ewm(span=9, adjust=False).mean()
    data['macd_hist'] = data['macd'] - data['macd_signal']

    fig = go.Figure()
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.05,
                        row_heights=[10, 10])

    # Add candlestick trace
    fig.add_trace(go.Candlestick(
        x=data.index if isinstance(data.index, pd.DatetimeIndex) else data['timestamp'],
        open=data['open'],
        high=data['high'],
        low=data['low'],
        close=data['close'],
        name='OHLC'))

    # add moving average traces
    fig.add_trace(go.Scatter(x=data.index if isinstance(data.index, pd.DatetimeIndex) else data['timestamp'],
                             y=data['MA5'],
                             opacity=0.7,
                             line=dict(color='blue', width=2),
                             name='MA 5'))
    fig.add_trace(go.Scatter(x=data.index if isinstance(data.index, pd.DatetimeIndex) else data['timestamp'],
                             y=data['MA20'],
                             opacity=0.7,
                             line=dict(color='orange', width=2),
                             name='MA 20'))

    # Plot MACD trace on 2nd row
    fig.add_trace(go.Scatter(x=data.index if isinstance(data.index, pd.DatetimeIndex) else data['timestamp'],
                             y=data['macd'],
                             line=dict(color='black', width=2),
                             name='MACD'), row=2, col=1)

    fig.add_trace(go.Scatter(x=data.index if isinstance(data.index, pd.DatetimeIndex) else data['timestamp'],
                             y=data['macd_signal'],
                             line=dict(color='skyblue', width=2),
                             name='MACD Signal'), row=2, col=1)

    colors = ['green' if val >= 0
              else 'red' for val in data['macd_hist']]

    fig.add_trace(go.Bar(x=data.index if isinstance(data.index, pd.DatetimeIndex) else data['timestamp'],
                         y=data['macd_hist'],
                         marker_color=colors,
                         name='Histogram'
                         ), row=2, col=1)

    # hide weekends and xaxes
    fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])], showgrid=False)
    fig.update_xaxes(visible=True, showticklabels=False)
    fig.update_yaxes(title_text="OHLC", showgrid=True, row=1, col=1,
                     title_font_color="#444", title_font_size=20)
    fig.update_yaxes(title_text="MACD/Signal/Hist", showgrid=True, row=2, col=1,
                     title_font_color="#444", title_font_size=20)
    fig.update_layout(height=900,
                      width=1000,
                      xaxis_rangeslider_visible=False,
                      title=f"{symbol}<br><sup>2025</sup>",
                      title_font_color="#f00", title_font_size=24)

    fig.update_layout({
        'plot_bgcolor': 'rgb(247,247,247)',
        'paper_bgcolor': 'rgb(247,247,247)'
    })

    return fig


# def create_candlestick_chart_simplified(
#         data: pd.DataFrame,
#         symbol: str,
#         indicators: Optional[Dict[str, Any]] = None
# ) -> go.Figure:
#     """Create a simplified candlestick chart.
#
#     Args:
#         data: DataFrame containing OHLCV data
#         symbol: The stock symbol
#         indicators: Optional dictionary of indicators to add to the chart
#
#     Returns:
#         go.Figure: The configured Plotly figure
#     """
#     # Calculate technical indicators
#     data = data.copy()
#
#     # Create figure
#     fig = go.Figure()
#
#     # Add candlestick trace
#     fig.add_trace(go.Candlestick(
#         x=data.index if isinstance(data.index, pd.DatetimeIndex) else data['timestamp'],
#         open=data['open'],
#         high=data['high'],
#         low=data['low'],
#         close=data['close'],
#         name='OHLC'))
#
#     # Configure layout
#     fig.update_layout(
#         height=600,  # Reduced height since we don't have subplots
#         width=1000,
#         xaxis_rangeslider_visible=False,
#         title=f"{symbol}<br><sup>2025</sup>",
#         title_font_color="#444",
#         title_font_size=24,
#         plot_bgcolor='rgb(247,247,247)',
#         paper_bgcolor='rgb(247,247,247)',
#         yaxis=dict(
#             title="Price",
#             title_font_color="#444",
#             title_font_size=20,
#             showgrid=True
#         ),
#         xaxis=dict(
#             rangebreaks=[dict(bounds=["sat", "mon"])],
#             showgrid=False,
#             showticklabels=True  # Show x-axis labels
#         )
#     )
#
#     return fig



import pandas as pd
import plotly.graph_objects as go
from typing import Optional, Dict, Any

def create_candlestick_chart_simplified(
        data: pd.DataFrame,
        symbol: str,
        indicators: Optional[Dict[str, Any]] = None
) -> go.Figure:
    """Create a simplified candlestick chart with time range selector limited to 2025.

    Args:
        data: DataFrame containing OHLCV data
        symbol: The stock symbol
        indicators: Optional dictionary of indicators to add to the chart

    Returns:
        go.Figure: The configured Plotly figure
    """
    # Ensure datetime index
    data = data.copy()
    if not isinstance(data.index, pd.DatetimeIndex):
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        data.set_index('timestamp', inplace=True)

    # Calculate bounds from data
    start_date = pd.Timestamp("2025-01-01")
    end_date = data.index.max()

    # Create figure
    fig = go.Figure()

    # Add candlestick trace
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['open'],
        high=data['high'],
        low=data['low'],
        close=data['close'],
        name='OHLC'))

    # Define range selector buttons limited to 2025
    range_selector_buttons = [
        dict(count=1, label="1M", step="month", stepmode="backward"),
        dict(count=3, label="3M", step="month", stepmode="backward"),
        dict(count=6, label="6M", step="month", stepmode="backward"),
        dict(step="year", stepmode="todate", label="YTD"),
        dict(count=1, label="1Y", step="year", stepmode="backward"),
        dict(step="all", label="All")
    ]

    # Configure layout
    fig.update_layout(
        height=600,
        width=1000,
        xaxis_rangeslider_visible=False,
        title=f"{symbol}<br><sup>2025</sup>",
        title_font_color="#444",
        title_font_size=24,
        #plot_bgcolor='rgb(247,247,247)',
        #paper_bgcolor='rgb(247,247,247)',
        yaxis=dict(
            title="Price",
            title_font_color="#444",
            title_font_size=20,
            showgrid=True
        ),
        xaxis=dict(
            range=[start_date, end_date],  # Limit initial view to 2025 only
            rangebreaks=[
                # Hide weekends
                dict(bounds=["sat", "mon"]),
                # Hide hours outside 9:30 AM to 4:00 PM
                dict(bounds=[16, 9.5], pattern="hour")
            ],
            showgrid=False,
            showticklabels=True,
            rangeselector=dict(
                buttons=range_selector_buttons,
                bgcolor='lightgray',
                x=0, xanchor='left',
                y=1.15, yanchor='top',
                font=dict(size=12)
            ),
            type="date"
        )
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


def display_chart_simplified(symbol: str, indicators: Optional[Dict[str, Any]] = None, force_refresh: bool = False):
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
        fig = create_candlestick_chart_simplified(data, symbol, indicators)
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        logger.error(f"Error displaying chart for {symbol}: {e}")
        st.error("Error loading chart. Please try again later.")