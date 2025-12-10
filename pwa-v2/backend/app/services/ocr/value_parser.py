"""
OCR Value Parser Module

Extracts and parses monetary values from OCR text.
Handles Brazilian currency format (R$ 1.234,56).

Author: RelatoRecibo Team
Created: 2025-12-09
"""

import re
from decimal import Decimal, InvalidOperation
from typing import Optional, List, Tuple
from loguru import logger


class ValueParser:
    """
    Parses monetary values from OCR text.

    Features:
    - Brazilian format support (R$ 1.234,56)
    - Multiple pattern matching
    - Value validation
    - Total/subtotal detection
    """

    # Common keywords that indicate a total value
    TOTAL_KEYWORDS = [
        "total",
        "valor total",
        "total geral",
        "total a pagar",
        "total líquido",
        "valor",
        "vlr",
        "vl total",
        "soma",
        "importância",
        "liquido",
        "líquido"
    ]

    # Patterns to match monetary values
    # Examples:
    # R$ 123,45
    # R$ 1.234,56
    # RS 123.45 (sometimes OCR mistakes $ for S)
    # 123,45
    VALUE_PATTERNS = [
        # With currency symbol
        r'R[\$S]\s*(\d{1,3}(?:\.\d{3})*,\d{2})',
        # Without currency, with thousand separator
        r'(?:^|\s)(\d{1,3}(?:\.\d{3})+,\d{2})(?:\s|$)',
        # Without currency, without thousand separator
        r'(?:^|\s)(\d{1,4},\d{2})(?:\s|$)',
    ]

    def extract_value(self, text: str) -> Optional[Decimal]:
        """
        Extract monetary value from OCR text.

        Args:
            text: OCR extracted text

        Returns:
            Decimal value or None if not found
        """
        # Find all potential values
        values = self._find_all_values(text)

        if not values:
            logger.warning("No values found in OCR text")
            return None

        # Try to find total value
        total = self._find_total_value(text, values)

        if total:
            logger.info(f"Found total value: {total}")
            return total

        # If no total found, return the largest value
        largest = max(values)
        logger.info(f"Using largest value: {largest}")
        return largest

    def _find_all_values(self, text: str) -> List[Decimal]:
        """
        Find all monetary values in text.

        Args:
            text: OCR text

        Returns:
            List of Decimal values found
        """
        values = []

        for pattern in self.VALUE_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)

            for match in matches:
                value_str = match.group(1)
                value = self._parse_brazilian_currency(value_str)

                if value and self._is_valid_value(value):
                    values.append(value)

        # Remove duplicates
        values = list(set(values))

        logger.debug(f"Found {len(values)} potential values: {values}")

        return values

    def _find_total_value(
        self,
        text: str,
        values: List[Decimal]
    ) -> Optional[Decimal]:
        """
        Try to identify the total value from context.

        Args:
            text: OCR text
            values: List of found values

        Returns:
            Total value or None
        """
        if not values:
            return None

        # Split text into lines
        lines = text.lower().split('\n')

        # Look for lines containing total keywords
        for line in lines:
            # Check if line contains a total keyword
            has_keyword = any(
                keyword in line
                for keyword in self.TOTAL_KEYWORDS
            )

            if not has_keyword:
                continue

            # Try to find a value in this line or next few lines
            for pattern in self.VALUE_PATTERNS:
                match = re.search(pattern, line, re.IGNORECASE)

                if match:
                    value_str = match.group(1)
                    value = self._parse_brazilian_currency(value_str)

                    if value and value in values:
                        return value

        return None

    def _parse_brazilian_currency(self, value_str: str) -> Optional[Decimal]:
        """
        Parse Brazilian currency format to Decimal.

        Args:
            value_str: String like "1.234,56" or "123,45"

        Returns:
            Decimal value or None if invalid
        """
        try:
            # Remove spaces
            value_str = value_str.strip()

            # Replace thousand separator (.) with nothing
            value_str = value_str.replace('.', '')

            # Replace decimal separator (,) with .
            value_str = value_str.replace(',', '.')

            # Convert to Decimal
            value = Decimal(value_str)

            return value

        except (InvalidOperation, ValueError) as e:
            logger.debug(f"Failed to parse value '{value_str}': {e}")
            return None

    def _is_valid_value(self, value: Decimal) -> bool:
        """
        Check if value is valid for a receipt.

        Args:
            value: Decimal value

        Returns:
            True if valid
        """
        # Value should be positive
        if value <= 0:
            return False

        # Value should be reasonable (between R$ 0.01 and R$ 1,000,000)
        if value < Decimal("0.01") or value > Decimal("1000000.00"):
            return False

        return True

    def extract_all_values(self, text: str) -> List[Decimal]:
        """
        Extract all valid monetary values from text.

        Args:
            text: OCR text

        Returns:
            List of all found values
        """
        return self._find_all_values(text)

    def parse_value(self, value_str: str) -> Optional[Decimal]:
        """
        Parse a single value string.

        Args:
            value_str: Value string (e.g., "123,45", "R$ 1.234,56")

        Returns:
            Decimal value or None
        """
        # Try to extract value using patterns
        for pattern in self.VALUE_PATTERNS:
            match = re.search(pattern, value_str, re.IGNORECASE)

            if match:
                return self._parse_brazilian_currency(match.group(1))

        # Try direct parsing
        return self._parse_brazilian_currency(value_str)
