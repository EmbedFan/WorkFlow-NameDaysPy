"""
Utility module for date handling and MM-DD format operations [REQ-0023].

Provides date parsing, validation, and formatting utilities.
"""

import re
from datetime import date, datetime
from typing import Tuple, Optional

from app.constants import NAMEDAY_DATE_FORMAT, NAMEDAY_DATE_PATTERN
from app.exceptions import DateFormatException


def format_date_as_nameday(date_obj: date) -> str:
    """
    Convert date object to MM-DD format for namedays [REQ-0023].
    
    Args:
        date_obj: Date object to convert
    
    Returns:
        Date string in MM-DD format
    
    Example:
        >>> date(2026, 3, 15)
        '03-15'
    """
    return date_obj.strftime("%m-%d")


def parse_nameday_date(date_str: str) -> Tuple[int, int]:
    """
    Parse MM-DD format string to month and day tuple.
    
    Does NOT validate - use is_valid_nameday_date() separately for validation.
    
    Args:
        date_str: Date string in MM-DD format
    
    Returns:
        Tuple of (month, day)
    
    Raises:
        DateFormatException: If date cannot be parsed
    
    Example:
        >>> parse_nameday_date("03-15")
        (3, 15)
    """
    try:
        parts = date_str.split("-")
        if len(parts) != 2:
            raise ValueError(f"Invalid format")
        month = int(parts[0])
        day = int(parts[1])
        return month, day
    except Exception as e:
        raise DateFormatException(f"Invalid date format. Expected MM-DD, got '{date_str}'", date_str) from e


def is_valid_nameday_date(date_str: str) -> bool:
    """
    Validate MM-DD format [REQ-0023, REQ-0040].
    
    Independent validation without circular dependencies.
    
    Args:
        date_str: String to validate
    
    Returns:
        True if valid MM-DD format, False otherwise
    """
    if not date_str or not isinstance(date_str, str):
        return False
    
    # Check regex pattern
    if not re.match(NAMEDAY_DATE_PATTERN, date_str):
        return False
    
    # Validate day range for month
    try:
        month, day = parse_nameday_date(date_str)
        days_in_month = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        return 1 <= day <= days_in_month[month - 1]
    except Exception:
        return False


def get_today_nameday_date() -> str:
    """
    Get today's date in MM-DD nameday format [REQ-0023].
    
    Returns:
        Today's date as MM-DD string
    
    Example:
        >>> get_today_nameday_date()  # if today is March 15, 2026
        '03-15'
    """
    today = date.today()
    return format_date_as_nameday(today)


def is_nameday_today(nameday_date: str) -> bool:
    """
    Check if a nameday date is today's date.
    
    Args:
        nameday_date: Nameday date in MM-DD format
    
    Returns:
        True if nameday is today, False otherwise
    """
    return nameday_date == get_today_nameday_date()


def get_days_until_nameday(nameday_date: str) -> int:
    """
    Calculate days until a nameday (0 = today, positive = future, negative = past year).
    
    Args:
        nameday_date: Nameday date in MM-DD format
    
    Returns:
        Number of days until nameday
    
    Raises:
        DateFormatException: If date format is invalid
    """
    if not is_valid_nameday_date(nameday_date):
        raise DateFormatException(f"Invalid nameday date: {nameday_date}", nameday_date)
    
    month, day = parse_nameday_date(nameday_date)
    today = date.today()
    
    try:
        nameday_this_year = date(today.year, month, day)
    except ValueError:
        # Handle leap day on non-leap years
        nameday_this_year = date(today.year, month, 28)
    
    delta = nameday_this_year - today
    
    if delta.days < 0:
        # Nameday already passed this year, calculate for next year
        try:
            nameday_next_year = date(today.year + 1, month, day)
        except ValueError:
            nameday_next_year = date(today.year + 1, month, 28)
        delta = nameday_next_year - today
    
    return delta.days


def get_nameday_display_text(nameday_date: str) -> str:
    """
    Get user-friendly display text for a nameday date.
    
    Args:
        nameday_date: Nameday date in MM-DD format
    
    Returns:
        Formatted display text
    """
    if not is_valid_nameday_date(nameday_date):
        return "Invalid date"
    
    month, day = parse_nameday_date(nameday_date)
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    
    return f"{month_names[month - 1]} {day}"


def format_datetime_for_display(dt: datetime) -> str:
    """
    Format datetime for user display.
    
    Args:
        dt: Datetime object to format
    
    Returns:
        Formatted datetime string
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def compare_nameday_dates(date1: str, date2: str) -> int:
    """
    Compare two MM-DD format dates.
    
    Args:
        date1: First date in MM-DD format
        date2: Second date in MM-DD format
    
    Returns:
        -1 if date1 < date2, 0 if equal, 1 if date1 > date2
    
    Raises:
        DateFormatException: If either date format is invalid
    """
    if not is_valid_nameday_date(date1):
        raise DateFormatException(f"Invalid date: {date1}", date1)
    if not is_valid_nameday_date(date2):
        raise DateFormatException(f"Invalid date: {date2}", date2)
    
    m1, d1 = parse_nameday_date(date1)
    m2, d2 = parse_nameday_date(date2)
    
    if m1 < m2 or (m1 == m2 and d1 < d2):
        return -1
    elif m1 > m2 or (m1 == m2 and d1 > d2):
        return 1
    else:
        return 0
