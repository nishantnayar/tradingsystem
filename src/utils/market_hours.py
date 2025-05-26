from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
import requests
from loguru import logger

from src.utils.config import get_config


class MarketHoursManager:
    """Manages market hours and trading calendar using Alpaca API."""

    def __init__(self):
        """Initialize with Alpaca API credentials."""
        config = get_config()
        alpaca_config = config["alpaca"]
        self.api_key = alpaca_config["api_key"]
        self.secret_key = alpaca_config["secret_key"]
        self.base_url = "https://paper-api.alpaca.markets/v2"

    def _make_request(self, endpoint: str, params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Make an authenticated request to Alpaca API."""
        headers = {
            "APCA-API-KEY-ID": self.api_key,
            "APCA-API-SECRET-KEY": self.secret_key
        }
        response = requests.get(f"{self.base_url}/{endpoint}", headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def is_market_open(self) -> bool:
        """
        Check if the market is currently open using /v2/clock endpoint.
        
        Returns:
            bool: True if market is open, False otherwise
        """
        try:
            logger.debug("Checking market status...")
            clock = self._make_request("clock")
            logger.debug(f"Market clock response: {clock}")
            return clock["is_open"]
        except Exception as e:
            logger.error(f"Error checking market status: {e}")
            return False

    def get_market_calendar(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get market calendar for a date range using /v2/calendar endpoint.
        
        Args:
            start_date: Start date for calendar (default: today)
            end_date: End date for calendar (default: today + 7 days)
            
        Returns:
            Dict containing calendar information
        """
        try:
            if start_date is None:
                start_date = datetime.now(timezone.utc)
            if end_date is None:
                end_date = start_date + timedelta(days=7)

            params = {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d")
            }
            
            calendar = self._make_request("calendar", params)
            return calendar
        except Exception as e:
            logger.error(f"Error fetching market calendar: {e}")
            return {}

    def get_next_market_open(self) -> Optional[datetime]:
        """
        Get the next market open time.
        
        Returns:
            datetime: Next market open time or None if error
        """
        try:
            clock = self._make_request("clock")
            next_open = datetime.fromisoformat(clock["next_open"].replace("Z", "+00:00"))
            return next_open
        except Exception as e:
            logger.error(f"Error getting next market open: {e}")
            return None

    def get_next_market_close(self) -> Optional[datetime]:
        """
        Get the next market close time.
        
        Returns:
            datetime: Next market close time or None if error
        """
        try:
            clock = self._make_request("clock")
            next_close = datetime.fromisoformat(clock["next_close"].replace("Z", "+00:00"))
            return next_close
        except Exception as e:
            logger.error(f"Error getting next market close: {e}")
            return None

    def is_trading_day(self, date: Optional[datetime] = None) -> bool:
        """
        Check if a given date is a trading day.
        
        Args:
            date: Date to check (default: today)
            
        Returns:
            bool: True if it's a trading day, False otherwise
        """
        try:
            if date is None:
                date = datetime.now(timezone.utc)
            
            calendar = self.get_market_calendar(date, date)
            return len(calendar) > 0
        except Exception as e:
            logger.error(f"Error checking trading day: {e}")
            return False

    def _parse_market_time(self, date: datetime, time_str: str) -> datetime:
        """Parse market time string into datetime object.
        
        Args:
            date: Base date for the time
            time_str: Time string in format 'HH:MM' or 'HH:MM:SS'
            
        Returns:
            datetime: Parsed datetime object
        """
        try:
            # Split time string into components
            time_parts = time_str.split(':')
            hour = int(time_parts[0])
            minute = int(time_parts[1])
            second = int(time_parts[2]) if len(time_parts) > 2 else 0
            
            # Create datetime object
            return date.replace(
                hour=hour,
                minute=minute,
                second=second,
                microsecond=0,
                tzinfo=timezone.utc
            )
        except Exception as e:
            logger.error(f"Error parsing market time {time_str}: {e}")
            raise

    def get_market_hours(self, date: Optional[datetime] = None) -> Dict[str, datetime]:
        """
        Get market open and close times for a specific date.
        Simplified version that assumes standard market hours (9:30 AM - 4:00 PM ET).
        
        Args:
            date: Date to check (default: today)
            
        Returns:
            Dict containing open and close times
        """
        try:
            current_time = datetime.now(timezone.utc)
            
            # Use current date in 2024
            if current_time.year > 2024:
                logger.warning(f"System time shows future year {current_time.year}. Using current date in 2024.")
                current_time = datetime(2024, current_time.month, current_time.day, 
                                      current_time.hour, current_time.minute, 
                                      current_time.second, current_time.microsecond,
                                      tzinfo=timezone.utc)
            
            if date is None:
                date = current_time
            elif date.tzinfo is None:
                # If date has no timezone, assume UTC
                date = date.replace(tzinfo=timezone.utc)
            
            # If date is in the future, use current time
            if date > current_time:
                logger.warning(f"Date {date} is in the future, using current time: {current_time}")
                date = current_time
            
            # Use current date in 2024
            if date.year > 2024:
                logger.warning(f"Date {date} is in future year {date.year}. Using current date in 2024.")
                date = datetime(2024, date.month, date.day, 
                              date.hour, date.minute, 
                              date.second, date.microsecond,
                              tzinfo=timezone.utc)
            
            logger.debug(f"Getting market hours for date: {date}")
            
            # Use standard market hours (9:30 AM - 4:00 PM ET)
            base_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            return {
                "open": base_date.replace(hour=13, minute=30, tzinfo=timezone.utc),  # 9:30 AM ET
                "close": base_date.replace(hour=20, minute=0, tzinfo=timezone.utc)   # 4:00 PM ET
            }
            
        except Exception as e:
            logger.error(f"Error getting market hours: {e}")
            # Fallback to standard market hours
            base_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            return {
                "open": base_date.replace(hour=13, minute=30, tzinfo=timezone.utc),  # 9:30 AM ET
                "close": base_date.replace(hour=20, minute=0, tzinfo=timezone.utc)   # 4:00 PM ET
            } 