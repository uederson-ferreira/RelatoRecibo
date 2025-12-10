"""
PDF Styles Module

Defines styles and formatting constants for PDF generation.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY


# Page configuration
PAGE_SIZE = A4
PAGE_WIDTH, PAGE_HEIGHT = PAGE_SIZE
MARGIN_LEFT = 2 * cm
MARGIN_RIGHT = 2 * cm
MARGIN_TOP = 2 * cm
MARGIN_BOTTOM = 2 * cm

# Content area
CONTENT_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT
CONTENT_HEIGHT = PAGE_HEIGHT - MARGIN_TOP - MARGIN_BOTTOM

# Colors
COLOR_PRIMARY = colors.HexColor("#2563EB")  # Blue
COLOR_SECONDARY = colors.HexColor("#64748B")  # Gray
COLOR_SUCCESS = colors.HexColor("#10B981")  # Green
COLOR_DANGER = colors.HexColor("#EF4444")  # Red
COLOR_TEXT = colors.HexColor("#1F2937")  # Dark gray
COLOR_TEXT_LIGHT = colors.HexColor("#6B7280")  # Light gray
COLOR_BACKGROUND = colors.HexColor("#F9FAFB")  # Light gray background
COLOR_BORDER = colors.HexColor("#E5E7EB")  # Border gray

# Fonts
FONT_NAME_REGULAR = "Helvetica"
FONT_NAME_BOLD = "Helvetica-Bold"
FONT_SIZE_TITLE = 24
FONT_SIZE_SUBTITLE = 18
FONT_SIZE_HEADING = 14
FONT_SIZE_BODY = 11
FONT_SIZE_SMALL = 9

# Spacing
SPACING_SMALL = 0.3 * cm
SPACING_MEDIUM = 0.5 * cm
SPACING_LARGE = 1 * cm
SPACING_XLARGE = 1.5 * cm

# Table configuration
TABLE_HEADER_BACKGROUND = COLOR_PRIMARY
TABLE_HEADER_TEXT = colors.white
TABLE_ROW_BACKGROUND = colors.white
TABLE_ALTERNATE_ROW_BACKGROUND = COLOR_BACKGROUND
TABLE_BORDER_COLOR = COLOR_BORDER
TABLE_BORDER_WIDTH = 1


def get_custom_styles():
    """
    Get custom paragraph styles for PDF generation.

    Returns:
        Dict with style names and ParagraphStyle objects
    """
    styles = getSampleStyleSheet()

    custom_styles = {
        # Title style
        "Title": ParagraphStyle(
            "CustomTitle",
            parent=styles["Title"],
            fontSize=FONT_SIZE_TITLE,
            textColor=COLOR_TEXT,
            fontName=FONT_NAME_BOLD,
            spaceAfter=SPACING_MEDIUM,
            alignment=TA_LEFT,
        ),

        # Subtitle style
        "Subtitle": ParagraphStyle(
            "CustomSubtitle",
            parent=styles["Heading2"],
            fontSize=FONT_SIZE_SUBTITLE,
            textColor=COLOR_SECONDARY,
            fontName=FONT_NAME_BOLD,
            spaceAfter=SPACING_SMALL,
            alignment=TA_LEFT,
        ),

        # Heading style
        "Heading": ParagraphStyle(
            "CustomHeading",
            parent=styles["Heading3"],
            fontSize=FONT_SIZE_HEADING,
            textColor=COLOR_TEXT,
            fontName=FONT_NAME_BOLD,
            spaceAfter=SPACING_SMALL,
            spaceBefore=SPACING_MEDIUM,
            alignment=TA_LEFT,
        ),

        # Body text style
        "Body": ParagraphStyle(
            "CustomBody",
            parent=styles["Normal"],
            fontSize=FONT_SIZE_BODY,
            textColor=COLOR_TEXT,
            fontName=FONT_NAME_REGULAR,
            spaceAfter=SPACING_SMALL,
            alignment=TA_JUSTIFY,
        ),

        # Small text style
        "Small": ParagraphStyle(
            "CustomSmall",
            parent=styles["Normal"],
            fontSize=FONT_SIZE_SMALL,
            textColor=COLOR_TEXT_LIGHT,
            fontName=FONT_NAME_REGULAR,
            spaceAfter=SPACING_SMALL,
        ),

        # Currency style (bold, green for positive)
        "Currency": ParagraphStyle(
            "CustomCurrency",
            parent=styles["Normal"],
            fontSize=FONT_SIZE_BODY,
            textColor=COLOR_SUCCESS,
            fontName=FONT_NAME_BOLD,
            alignment=TA_RIGHT,
        ),

        # Date style
        "Date": ParagraphStyle(
            "CustomDate",
            parent=styles["Normal"],
            fontSize=FONT_SIZE_BODY,
            textColor=COLOR_TEXT_LIGHT,
            fontName=FONT_NAME_REGULAR,
        ),

        # Description style
        "Description": ParagraphStyle(
            "CustomDescription",
            parent=styles["Normal"],
            fontSize=FONT_SIZE_BODY,
            textColor=COLOR_TEXT,
            fontName=FONT_NAME_REGULAR,
        ),

        # Footer style
        "Footer": ParagraphStyle(
            "CustomFooter",
            parent=styles["Normal"],
            fontSize=FONT_SIZE_SMALL,
            textColor=COLOR_TEXT_LIGHT,
            fontName=FONT_NAME_REGULAR,
            alignment=TA_CENTER,
        ),
    }

    return custom_styles
