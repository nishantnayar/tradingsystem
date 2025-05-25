from datetime import datetime, timezone
import streamlit as st
from loguru import logger
from pytz import timezone as pytz_timezone
from typing import Optional, Dict, Any

from src.utils.market_hours import MarketHoursManager
from src.ui.components.date_display import format_datetime_est_to_cst


def get_ordinal_suffix(day):
    """Return ordinal suffix for a day (st, nd, rd, th)"""
    if 11 <= day <= 13:
        return 'th'
    return {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')


def format_datetime_cst(dt):
    """Format datetime in CST as '24th May, 2025 8:08 PM'"""
    cst_zone = pytz_timezone('America/Chicago')

    # Handle both timezone-naive and timezone-aware datetimes
    if dt.tzinfo is None:
        dt = pytz_timezone('UTC').localize(dt)

    cst_time = dt.astimezone(cst_zone)

    # Get components for custom formatting
    day = cst_time.day
    suffix = get_ordinal_suffix(day)
    month = cst_time.strftime("%B")
    year = cst_time.year
    hour = cst_time.strftime("%I").lstrip("0") or "12"  # Remove leading zero
    minute = cst_time.strftime("%M")
    ampm = cst_time.strftime("%p")

    return f"{day}{suffix} {month}, {year} {hour}:{minute} {ampm}"


def display_market_status_section(is_open: bool, current_time: datetime) -> None:
    """Display the market status section.
    
    Args:
        is_open: Whether the market is currently open
        current_time: Current time in UTC
    """
    st.subheader("Market Status")
    
    if is_open:
        st.success("Market is OPEN")
    else:
        st.error("Market is CLOSED")
    
    st.write(f"Current Time: {format_datetime_est_to_cst(current_time)}")


def display_next_events(next_open: Optional[datetime], next_close: Optional[datetime]) -> None:
    """Display next market events.
    
    Args:
        next_open: Next market open time
        next_close: Next market close time
    """
    st.subheader("Next Events")
    
    if next_open:
        st.write(f"Next Open: {format_datetime_est_to_cst(next_open)}")
    if next_close:
        st.write(f"Next Close: {format_datetime_est_to_cst(next_close)}")


def display_market_hours(hours: Optional[Dict[str, datetime]]) -> None:
    """Display today's market hours.
    
    Args:
        hours: Dictionary containing market open and close times
    """
    st.subheader("Today's Market Hours")
    
    if hours:
        col1, col2 = st.columns(2)
        with col1:
            time_str = format_datetime_est_to_cst(hours['open']).split(', ')[-1]
            st.write(f"Open: {time_str}")
        with col2:
            time_str = format_datetime_est_to_cst(hours['close']).split(', ')[-1]
            st.write(f"Close: {time_str}")
    else:
        st.warning("No market hours available for today")


def display_market_status() -> None:
    """Display current market status and hours with times in CST."""
    try:
        market_hours = MarketHoursManager()
        current_time = datetime.now(timezone.utc)
        
        # Create two columns for status and next events
        col1, col2 = st.columns(2)
        
        with col1:
            display_market_status_section(
                market_hours.is_market_open(),
                current_time
            )
        
        with col2:
            display_next_events(
                market_hours.get_next_market_open(),
                market_hours.get_next_market_close()
            )
        
        # Display market hours
        display_market_hours(market_hours.get_market_hours())

    except Exception as e:
        logger.error(f"Error displaying market status: {e}")
        st.error("Error fetching market status. Please try again later.")