"""
Analysis page for technical analysis and backtesting.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

from plotly.subplots import make_subplots

from src.data.data_manager import DataManager
from src.data.symbol_manager import SymbolManager


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
            data_manager = DataManager()
            data = data_manager.get_latest_data(selected_symbol)
            
            if data is not None and not data.empty:
                # Create price chart with indicators
                fig = create_analysis_chart(
                    data,
                    show_sma=show_sma,
                    sma_period=sma_period if show_sma else None,
                    show_rsi=show_rsi,
                    rsi_period=rsi_period if show_rsi else None
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Display technical metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Current Price", f"${data['close'].iloc[-1]:.2f}")
                with col2:
                    st.metric("24h Change", f"{((data['close'].iloc[-1] / data['close'].iloc[-2] - 1) * 100):.2f}%")
                with col3:
                    st.metric("Volume", f"{data['volume'].iloc[-1]:,}")
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


def create_analysis_chart(
    data: pd.DataFrame,
    show_sma: bool = True,
    sma_period: int = 20,
    show_rsi: bool = True,
    rsi_period: int = 14
) -> go.Figure:
    """Create a technical analysis chart with indicators."""
    # Create figure with secondary y-axis
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.7, 0.3]
    )
    
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
        row=1, col=1
    )
    
    # Add SMA if enabled
    if show_sma:
        sma = data['close'].rolling(window=sma_period).mean()
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=sma,
                name=f"SMA {sma_period}",
                line=dict(color='blue')
            ),
            row=1, col=1
        )
    
    # Add RSI if enabled
    if show_rsi:
        # Calculate RSI
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=rsi,
                name=f"RSI {rsi_period}",
                line=dict(color='purple')
            ),
            row=2, col=1
        )
        
        # Add RSI levels
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
    
    # Update layout
    fig.update_layout(
        title="Technical Analysis",
        xaxis_title="Date",
        yaxis_title="Price",
        height=800,
        showlegend=True
    )
    
    return fig 