"""
PDF Utilities Module

Utility functions for PDF operations.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from io import BytesIO
from typing import Optional
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def create_empty_pdf() -> BytesIO:
    """
    Create an empty PDF document.

    Returns:
        BytesIO buffer with empty PDF
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


def validate_pdf_bytes(pdf_bytes: bytes) -> bool:
    """
    Validate if bytes represent a valid PDF.

    Args:
        pdf_bytes: PDF bytes to validate

    Returns:
        True if valid PDF, False otherwise
    """
    if not pdf_bytes:
        return False

    # Check PDF header
    pdf_header = pdf_bytes[:4]
    return pdf_header == b"%PDF"


def get_pdf_size(pdf_bytes: bytes) -> int:
    """
    Get PDF size in bytes.

    Args:
        pdf_bytes: PDF bytes

    Returns:
        Size in bytes
    """
    return len(pdf_bytes)


def format_pdf_filename(report_name: str, report_id: Optional[str] = None) -> str:
    """
    Format PDF filename.

    Args:
        report_name: Report name
        report_id: Optional report ID

    Returns:
        Formatted filename (e.g., "relatorio_viagem_sao_paulo.pdf")
    """
    # Clean report name
    import re
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', report_name)
    cleaned = re.sub(r'\s+', '_', cleaned)
    cleaned = cleaned.lower()

    # Add report ID if provided
    if report_id:
        cleaned = f"{cleaned}_{report_id[:8]}"

    return f"{cleaned}.pdf"
