from datetime import datetime, timezone
import streamlit as st
from loguru import logger
from pytz import timezone as pytz_timezone

from src.utils.market_hours import MarketHoursManager


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


def display_market_status():
    """Display current market status and hours with times in CST."""
    try:
        market_hours = MarketHoursManager()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Market Status")
            is_open = market_hours.is_market_open()

            if is_open:
                st.success("Market is OPEN")
            else:
                st.error("Market is CLOSED")

            current_time = datetime.now(timezone.utc)
            st.write(f"Current Time: {format_datetime_cst(current_time)}")

        with col2:
            st.subheader("Next Events")
            next_open = market_hours.get_next_market_open()
            next_close = market_hours.get_next_market_close()

            if next_open:
                st.write(f"Next Open: {format_datetime_cst(next_open)}")
            if next_close:
                st.write(f"Next Close: {format_datetime_cst(next_close)}")

        st.subheader("Today's Market Hours")
        hours = market_hours.get_market_hours()

        if hours:
            col3, col4 = st.columns(2)
            with col3:
                time_str = format_datetime_cst(hours['open']).split(', ')[-1]
                st.write(f"Open: {time_str}")
            with col4:
                time_str = format_datetime_cst(hours['close']).split(', ')[-1]
                st.write(f"Close: {time_str}")
        else:
            st.warning("No market hours available for today")

    except Exception as e:
        logger.error(f"Error displaying market status: {e}")
        st.error("Error fetching market status. Please try again later.")