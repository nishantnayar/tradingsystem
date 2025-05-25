import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from pytz import timezone as pytz_timezone
from loguru import logger
from sqlalchemy import text
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from typing import Optional, Dict, Any

from src.database.db_manager import DatabaseManager
from src.ui.components.date_display import format_datetime_est_to_cst


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


def display_market_data(symbol: str, lookback_days: int = 30) -> None:
    """Display market data for a symbol.
    
    Args:
        symbol: The stock symbol to display data for
        lookback_days: Number of days of historical data to display
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
                AND timestamp > :start_date
                ORDER BY timestamp DESC
            """)

            start_date = datetime.now() - timedelta(days=lookback_days)
            result = session.execute(query, {
                'symbol': symbol,
                'start_date': start_date
            })
            
            data = pd.DataFrame(
                result.fetchall(),
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )

            if data.empty:
                st.warning(f"No data available for {symbol}")
                return

            # Display metrics
            create_metrics_display(data)

            # Display timestamp
            st.subheader('Market Data')
            updated_date = data['timestamp'].iloc[0]
            st.write(f'As of: {format_datetime_est_to_cst(updated_date)}')

            # Display data table
            create_data_table(data)

    except Exception as e:
        logger.error(f"Error displaying market data for {symbol}: {e}")
        st.error("Error loading market data. Please try again later.")
