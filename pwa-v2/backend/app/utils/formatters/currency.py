"""
Currency Formatter Module

Utilities for formatting currency values in Brazilian Real (BRL).

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from decimal import Decimal
from typing import Union


def format_brl(value: Union[Decimal, float, int]) -> str:
    """
    Format value as Brazilian Real currency.

    Args:
        value: Numeric value to format

    Returns:
        Formatted currency string (e.g., "R$ 1.250,50")

    Example:
        >>> format_brl(1250.50)
        'R$ 1.250,50'
        >>> format_brl(Decimal("0.99"))
        'R$ 0,99'
        >>> format_brl(1000000)
        'R$ 1.000.000,00'
    """
    if isinstance(value, (int, float)):
        value = Decimal(str(value))

    # Format with 2 decimal places
    formatted = f"{value:,.2f}"

    # Replace comma (thousands) with temporary placeholder
    formatted = formatted.replace(",", "TEMP")

    # Replace dot (decimal) with comma
    formatted = formatted.replace(".", ",")

    # Replace temporary placeholder with dot
    formatted = formatted.replace("TEMP", ".")

    return f"R$ {formatted}"


def format_brl_short(value: Union[Decimal, float, int]) -> str:
    """
    Format value as BRL with abbreviations for large numbers.

    Args:
        value: Numeric value to format

    Returns:
        Abbreviated currency string (e.g., "R$ 1,2 mil", "R$ 1,5 M")

    Example:
        >>> format_brl_short(1250)
        'R$ 1,3 mil'
        >>> format_brl_short(1500000)
        'R$ 1,5 M'
        >>> format_brl_short(100)
        'R$ 100,00'
    """
    if isinstance(value, (int, float)):
        value = Decimal(str(value))

    abs_value = abs(value)

    if abs_value >= 1_000_000_000:  # Bilhões
        return f"R$ {value / 1_000_000_000:,.1f} B".replace(".", ",")
    elif abs_value >= 1_000_000:  # Milhões
        return f"R$ {value / 1_000_000:,.1f} M".replace(".", ",")
    elif abs_value >= 1_000:  # Milhares
        return f"R$ {value / 1_000:,.1f} mil".replace(".", ",")
    else:
        return format_brl(value)


def parse_brl(value: str) -> Decimal:
    """
    Parse Brazilian Real currency string to Decimal.

    Args:
        value: Currency string (e.g., "R$ 1.250,50" or "1.250,50")

    Returns:
        Decimal value

    Raises:
        ValueError: If string cannot be parsed

    Example:
        >>> parse_brl("R$ 1.250,50")
        Decimal('1250.50')
        >>> parse_brl("1.250,50")
        Decimal('1250.50')
        >>> parse_brl("R$ 0,99")
        Decimal('0.99')
    """
    # Remove currency symbol and spaces
    cleaned = value.replace("R$", "").replace(" ", "").strip()

    # Replace thousands separator (dot) with nothing
    cleaned = cleaned.replace(".", "")

    # Replace decimal separator (comma) with dot
    cleaned = cleaned.replace(",", ".")

    try:
        return Decimal(cleaned)
    except Exception as e:
        raise ValueError(f"Invalid currency string: {value}") from e
