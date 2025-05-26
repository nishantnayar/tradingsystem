"""
Analysis page for technical analysis and backtesting.
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from loguru import logger

from src.data.symbol_manager import SymbolManager
from src.ui.components.chart_display import display_chart
from src.ui.state.market_data_state import (
    get_market_data,
    get_latest_price,
    get_price_change,
    get_last_refresh_time,
    get_company_info
)
from src.ui.components.data_display import format_refresh_time




def render_analysis():
    """Render the analysis page."""
    st.title("Technical Analysis")

    tab0, tab1, tab2 = st.tabs(["Company Info","Indicators", "BackTesting"])

    with tab0:
        st.header("Company Info")
        
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
            # Symbol selector
            symbols = SymbolManager.get_active_symbols()
            selected_symbol = st.selectbox(
                "Select Symbol",
                options=symbols,
                index=0 if symbols else None
            )

            # Store selected symbol in session state
            if selected_symbol:
                st.session_state.selected_symbol = selected_symbol

        # Add a separator
        st.markdown("---")

        # Display company information
        if selected_symbol:
            company_info = get_company_info(selected_symbol)
            if company_info:
                col1, col2, col3 = st.columns([3, 3, 3])
                with col1:
                    st.write("Company Name")
                    st.write(f"**{company_info['company_name']}**")
                with col2:
                    st.write("Sector")
                    st.write(f"**{company_info['sector']}**")
                with col3:
                    st.write("Industry")
                    st.write(f"**{company_info['industry']}**")

                st.write("Address")
                if company_info['address2'] is not None:
                    st.write(f"**{company_info['address1']+ ', ' +company_info['address2']+', ' +company_info['city']+', '+company_info['state']}**")
                else:
                    st.write(f"**{company_info['address1']+ ', ' +company_info['city']+', '+company_info['state']}**")
            else:
                st.warning("No company information available for this symbol.")
        else:
            st.info("Please select a symbol to view company information.")

    with tab1:

        # Controls section
        st.subheader("Controls")
        st.write(f"Showing Data for {selected_symbol}")

        # Add a separator
        st.markdown("---")

        # Technical indicators section
        st.subheader("Technical Indicators")
        col1, col2 = st.columns(2)

        with col1:
            show_sma = st.checkbox("Simple Moving Average", value=True)
            if show_sma:
                sma_period = st.slider("SMA Period", 5, 200, 20)

        with col2:
            show_rsi = st.checkbox("RSI", value=True)
            if show_rsi:
                rsi_period = st.slider("RSI Period", 5, 30, 14)

        # Add a separator
        st.markdown("---")

        # Main content area
        if selected_symbol:
            st.header(f"Technical Analysis: {selected_symbol}")

            # Get data from state management
            data = get_market_data(
                selected_symbol,
                force_refresh=st.session_state.get('force_refresh', False)
            )

            # Reset force refresh flag
            if 'force_refresh' in st.session_state:
                st.session_state.force_refresh = False

            if data is not None and not data.empty:
                # Display technical metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    current_price = get_latest_price(selected_symbol)
                    if current_price is not None:
                        st.metric("Current Price", f"${current_price:.2f}")
                with col2:
                    price_change = get_price_change(selected_symbol)
                    if price_change is not None:
                        st.metric("24h Change", f"{price_change:.2f}%")
                with col3:
                    st.metric("Volume", f"{data['volume'].iloc[0]:,}")

                # Configure indicators based on settings
                indicators = {}
                if show_sma:
                    indicators['sma'] = {'period': sma_period}
                if show_rsi:
                    indicators['rsi'] = {'period': rsi_period}

                # Display chart with selected indicators
                display_chart(
                    selected_symbol,
                    indicators=indicators,
                    force_refresh=st.session_state.get('force_refresh', False)
                )
            else:
                st.warning(f"No data available for {selected_symbol}")
        else:
            st.info("Please select a symbol to view technical analysis")

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