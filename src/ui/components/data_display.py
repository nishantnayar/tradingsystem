import streamlit as st
import pandas as pd
from loguru import logger

from src.data.data_manager import DataManager


def display_market_data(symbol: str):
    """Display market data for a symbol.
    
    Args:
        symbol: The stock symbol to display data for
    """
    try:
        data_manager = DataManager()
        data = data_manager.get_latest_data(symbol)
        
        if data is None or data.empty:
            st.warning(f"No data available for {symbol}")
            return
            
        # Display latest price metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Open", f"${data['open'].iloc[-1]:.2f}")
        with col2:
            st.metric("High", f"${data['high'].iloc[-1]:.2f}")
        with col3:
            st.metric("Low", f"${data['low'].iloc[-1]:.2f}")
        with col4:
            st.metric("Close", f"${data['close'].iloc[-1]:.2f}")
            
        # Display volume
        st.metric("Volume", f"{data['volume'].iloc[-1]:,}")
        
        # Display recent data table
        st.subheader("Recent Data")
        display_data = data.tail(10).copy()
        display_data.index = display_data.index.strftime('%Y-%m-%d %H:%M:%S')
        st.dataframe(display_data, use_container_width=True)
        
    except Exception as e:
        logger.error(f"Error displaying market data for {symbol}: {e}")
        st.error("Error loading market data. Please try again later.") 