import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from loguru import logger

from src.data.data_manager import DataManager


def display_chart(symbol: str):
    """Display price chart for a symbol.
    
    Args:
        symbol: The stock symbol to display chart for
    """
    try:
        data_manager = DataManager()
        data = data_manager.get_latest_data(symbol)
        
        if data is None or data.empty:
            st.warning(f"No data available for {symbol}")
            return
            
        # Create figure with secondary y-axis
        fig = make_subplots(rows=2, cols=1, 
                           shared_xaxes=True,
                           vertical_spacing=0.03,
                           row_heights=[0.7, 0.3])

        # Add candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['open'],
                high=data['high'],
                low=data['low'],
                close=data['close'],
                name='Price'
            ),
            row=1, col=1
        )

        # Add volume bar chart
        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data['volume'],
                name='Volume'
            ),
            row=2, col=1
        )

        # Update layout
        fig.update_layout(
            title=f'{symbol} Price Chart',
            yaxis_title='Price',
            yaxis2_title='Volume',
            xaxis_rangeslider_visible=False,
            height=600
        )

        # Update y-axes labels
        fig.update_yaxes(title_text="Price", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)

        # Display the chart
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        logger.error(f"Error displaying chart for {symbol}: {e}")
        st.error("Error loading chart. Please try again later.") 