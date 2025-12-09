"""
Date Formatter Module

Utilities for formatting dates in Brazilian format.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from datetime import datetime, date
from typing import Union


def format_date_br(value: Union[datetime, date, str]) -> str:
    """
    Format date in Brazilian format (DD/MM/YYYY).

    Args:
        value: Date to format (datetime, date, or ISO string)

    Returns:
        Formatted date string (e.g., "15/01/2025")

    Example:
        >>> format_date_br(date(2025, 1, 15))
        '15/01/2025'
        >>> format_date_br("2025-01-15")
        '15/01/2025'
    """
    if isinstance(value, str):
        value = datetime.fromisoformat(value).date()
    elif isinstance(value, datetime):
        value = value.date()

    return value.strftime("%d/%m/%Y")


def format_datetime_br(value: Union[datetime, str]) -> str:
    """
    Format datetime in Brazilian format (DD/MM/YYYY HH:MM).

    Args:
        value: Datetime to format (datetime or ISO string)

    Returns:
        Formatted datetime string (e.g., "15/01/2025 14:30")

    Example:
        >>> format_datetime_br(datetime(2025, 1, 15, 14, 30))
        '15/01/2025 14:30'
    """
    if isinstance(value, str):
        value = datetime.fromisoformat(value)

    return value.strftime("%d/%m/%Y %H:%M")


def format_datetime_full_br(value: Union[datetime, str]) -> str:
    """
    Format datetime with seconds (DD/MM/YYYY HH:MM:SS).

    Args:
        value: Datetime to format

    Returns:
        Formatted datetime string (e.g., "15/01/2025 14:30:45")

    Example:
        >>> format_datetime_full_br(datetime(2025, 1, 15, 14, 30, 45))
        '15/01/2025 14:30:45'
    """
    if isinstance(value, str):
        value = datetime.fromisoformat(value)

    return value.strftime("%d/%m/%Y %H:%M:%S")
