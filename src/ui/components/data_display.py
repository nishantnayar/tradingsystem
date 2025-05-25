import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from pytz import timezone as pytz_timezone
from loguru import logger
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from typing import Optional, Dict, Any

from src.ui.state.market_data_state import get_market_data
from src.ui.components.date_display import format_datetime_est_to_cst


def format_refresh_time(dt: datetime) -> str:
    """Format refresh time in CST timezone consistently across the UI.
    
    Args:
        dt: The datetime to format (assumed to be in CST)
        
    Returns:
        str: Formatted datetime string in CST
    """
    # Ensure the datetime is in CST
    cst_zone = pytz_timezone('US/Central')
    if dt.tzinfo is None:
        dt = cst_zone.localize(dt)
    else:
        dt = dt.astimezone(cst_zone)
    
    # Format the datetime
    day = dt.day
    suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th') if day not in (11, 12, 13) else 'th'
    month = dt.strftime("%B")
    year = dt.year
    hour = dt.strftime("%I").lstrip("0") or "12"  # Remove leading zero
    minute = dt.strftime("%M")
    ampm = dt.strftime("%p")
    
    return f"{day}{suffix} {month}, {year} {hour}:{minute} {ampm}"


def create_metrics_display(data: pd.DataFrame) -> None:
    """Display price metrics in a row of columns.
    
    Args:
        data: DataFrame containing market data
    """
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Open", f"${data['open'].iloc[0]:.2f}")
    with col2:
        st.metric("High", f"${data['high'].iloc[0]:.2f}")
    with col3:
        st.metric("Low", f"${data['low'].iloc[0]:.2f}")
    with col4:
        st.metric("Close", f"${data['close'].iloc[0]:.2f}")
    with col5:
        st.metric("Volume", f"{data['volume'].iloc[0]:,}")


def create_data_table(data: pd.DataFrame) -> None:
    """Display data in an interactive table using AgGrid.
    
    Args:
        data: DataFrame containing market data
    """
    gb = GridOptionsBuilder.from_dataframe(data)
    gb.configure_pagination(enabled=True, paginationPageSize=10)
    gridoptions_table = gb.build()

    AgGrid(
        data,
        gridOptions=gridoptions_table,
        enable_enterprise_modules=True,
        use_container_width=True,
        fit_columns_on_grid_load=True
    )


def display_market_data(symbol: str, force_refresh: bool = False) -> None:
    """Display market data for a symbol.
    
    Args:
        symbol: The stock symbol to display data for
        force_refresh: Whether to force a refresh of the data
    """
    try:
        # Get data from state management
        data = get_market_data(symbol, force_refresh)
        
        if data is None or data.empty:
            st.warning(f"No data available for {symbol}")
            return

        # Display metrics
        create_metrics_display(data)

        # Display timestamp
        st.subheader('Market Data')
        updated_date = data['timestamp'].iloc[0]
        st.write(f'As of: {format_refresh_time(updated_date)}')

        # Display data table
        create_data_table(data)

    except Exception as e:
        logger.error(f"Error displaying market data for {symbol}: {e}")
        st.error("Error loading market data. Please try again later.")
