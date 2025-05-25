from datetime import datetime
from pytz import timezone as pytz_timezone
from typing import Union


def get_ordinal_suffix(day: int) -> str:
    """Return ordinal suffix for a day (st, nd, rd, th)

    Args:
        day: The day of the month (1-31)

    Returns:
        str: The appropriate ordinal suffix
    """
    if 11 <= day <= 13:
        return 'th'
    return {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')


def format_datetime_est_to_cst(dt: Union[datetime, str],
                               input_tz: str = 'US/Eastern') -> str:
    """Convert datetime from EST to CST and format as '24th May, 2025 8:08 PM'

    Args:
        dt: Either a datetime object or ISO format string (assumed to be in EST)
        input_tz: Timezone of the input if it's naive (default: 'US/Eastern')

    Returns:
        str: Formatted datetime string in CST

    Raises:
        ValueError: If input format is invalid
    """
    # Convert string to datetime if needed
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except ValueError as e:
            raise ValueError("Invalid datetime string format. Expected ISO format.") from e

    est_zone = pytz_timezone(input_tz)
    cst_zone = pytz_timezone('US/Central')

    # Handle timezone-naive datetimes by assuming they're EST
    if dt.tzinfo is None:
        dt = est_zone.localize(dt)
    else:
        # Convert to EST first if it's in another timezone
        dt = dt.astimezone(est_zone)

    # Convert to CST
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


def get_current_cst() -> datetime:
    """Get current time in CST timezone

    Returns:
        datetime: Current datetime in CST timezone
    """
    return datetime.now(pytz_timezone('US/Central'))


def get_current_cst_formatted() -> str:
    """Get current time in CST formatted as '24th May, 2025 8:08 PM'

    Returns:
        str: Formatted current CST datetime
    """
    return format_datetime_est_to_cst(get_current_cst())


def convert_est_to_cst(dt: Union[datetime, str]) -> datetime:
    """Convert a datetime from EST to CST

    Args:
        dt: Either a datetime object or ISO format string (assumed to be in EST)

    Returns:
        datetime: The converted datetime in CST
    """
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)

    est_zone = pytz_timezone('US/Eastern')
    cst_zone = pytz_timezone('US/Central')

    if dt.tzinfo is None:
        dt = est_zone.localize(dt)

    return dt.astimezone(cst_zone)