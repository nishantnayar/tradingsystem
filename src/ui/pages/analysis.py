"""
Analysis page for technical analysis and backtesting.
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from loguru import logger
from sqlalchemy import text

from src.data.symbol_manager import SymbolManager
from src.ui.components.chart_display import display_chart
from src.database.db_manager import DatabaseManager


def render_analysis():
    """Render the analysis page."""
    st.title("Technical Analysis")
    
    # Sidebar controls
    with st.sidebar:
        st.header("Analysis Settings")
        
        # Symbol selector
        symbols = SymbolManager.get_active_symbols()
        selected_symbol = st.selectbox(
            "Select Symbol",
            options=symbols,
            index=0 if symbols else None
        )
        
        # Timeframe selector
        timeframe = st.selectbox(
            "Timeframe",
            options=["1h", "4h", "1d"],
            index=0
        )
        
        # Date range selector
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        date_range = st.date_input(
            "Date Range",
            value=(start_date, end_date),
            max_value=end_date
        )
        
        # Technical indicators
        st.subheader("Technical Indicators")
        show_sma = st.checkbox("Simple Moving Average", value=True)
        if show_sma:
            sma_period = st.slider("SMA Period", 5, 200, 20)
        
        show_rsi = st.checkbox("RSI", value=True)
        if show_rsi:
            rsi_period = st.slider("RSI Period", 5, 30, 14)
    
    # Main content area with tabs
    tab1, tab2 = st.tabs(["Technical Analysis", "Backtesting"])
    
    with tab1:
        if selected_symbol:
            st.header(f"Technical Analysis: {selected_symbol}")
            
            # Get data
            db = DatabaseManager()
            with db.get_session() as session:
                query = text("""
                    SELECT timestamp, open, high, low, close, volume
                    FROM market_data
                    WHERE symbol = :symbol
                    AND timestamp > '2025-01-01'
                    ORDER BY timestamp DESC
                """)

                result = session.execute(query, {'symbol': selected_symbol})
                data = pd.DataFrame(
                    result.fetchall(),
                    columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
                )

                if data is not None and not data.empty:
                    # Display technical metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Current Price", f"${data['close'].iloc[-1]:.2f}")
                    with col2:
                        st.metric("24h Change", f"{((data['close'].iloc[-1] / data['close'].iloc[-2] - 1) * 100):.2f}%")
                    with col3:
                        st.metric("Volume", f"{data['volume'].iloc[-1]:,}")

                    # Configure indicators based on sidebar settings
                    indicators = {}
                    if show_sma:
                        indicators['sma'] = {'period': sma_period}
                    if show_rsi:
                        indicators['rsi'] = {'period': rsi_period}

                    # Display chart with selected indicators
                    display_chart(selected_symbol, indicators=indicators)
                else:
                    st.warning(f"No data available for {selected_symbol}")
    
    with tab2:
        st.header("Backtesting")
        st.write("Backtesting functionality will be implemented here.")
        
        # Placeholder for backtesting controls
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Strategy Parameters")
            st.number_input("Initial Capital", value=100000)
            st.number_input("Position Size (%)", value=10)
        
        with col2:
            st.subheader("Performance Metrics")
            st.metric("Total Return", "+25.5%")
            st.metric("Sharpe Ratio", "1.8")
            st.metric("Max Drawdown", "-12.3%") 