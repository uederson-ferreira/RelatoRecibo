"""
Report PDF Template Module

Template for generating report PDFs with receipts.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from decimal import Decimal
from typing import List, Dict, Any, Optional
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image as RLImage, KeepTogether
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from loguru import logger

from app.services.pdf.templates.styles import (
    get_custom_styles, PAGE_WIDTH, PAGE_HEIGHT,
    MARGIN_LEFT, MARGIN_RIGHT, MARGIN_TOP, MARGIN_BOTTOM,
    COLOR_PRIMARY, COLOR_TEXT, COLOR_TEXT_LIGHT, COLOR_BACKGROUND,
    COLOR_BORDER, TABLE_HEADER_BACKGROUND, TABLE_HEADER_TEXT,
    TABLE_ROW_BACKGROUND, TABLE_ALTERNATE_ROW_BACKGROUND,
    TABLE_BORDER_COLOR, TABLE_BORDER_WIDTH,
    SPACING_SMALL, SPACING_MEDIUM, SPACING_LARGE
)
from app.utils.formatters.currency import format_brl
from app.utils.formatters.date import format_date_br, format_datetime_br


class ReportPDFTemplate:
    """
    Template for generating report PDFs.

    Features:
    - Professional header with report information
    - Receipts table with images
    - Summary section with totals
    - Footer with generation date
    """

    def __init__(self):
        """Initialize the template."""
        self.styles = get_custom_styles()

    def generate(
        self,
        report: Dict[str, Any],
        receipts: List[Dict[str, Any]],
        user_name: Optional[str] = None
    ) -> BytesIO:
        """
        Generate PDF document for a report.

        Args:
            report: Report data dictionary
            receipts: List of receipt dictionaries
            user_name: Optional user name for header

        Returns:
            BytesIO buffer with PDF content
        """
        buffer = BytesIO()

        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=MARGIN_RIGHT,
            leftMargin=MARGIN_LEFT,
            topMargin=MARGIN_TOP,
            bottomMargin=MARGIN_BOTTOM,
        )

        # Build story (content)
        story = []

        # Header
        story.extend(self._build_header(report, user_name))

        # Summary section
        story.extend(self._build_summary(report, receipts))

        # Receipts table
        story.extend(self._build_receipts_table(receipts))

        # Footer
        story.extend(self._build_footer())

        # Build PDF
        doc.build(story)

        # Reset buffer position
        buffer.seek(0)
        return buffer

    def _build_header(
        self,
        report: Dict[str, Any],
        user_name: Optional[str] = None
    ) -> List:
        """Build PDF header section."""
        elements = []

        # Title
        title_style = self.styles["Title"]
        title = Paragraph(f"<b>Relatório de Despesas</b>", title_style)
        elements.append(title)
        elements.append(Spacer(1, SPACING_SMALL))

        # Report name
        subtitle_style = self.styles["Subtitle"]
        report_name = Paragraph(
            f"<b>{report.get('name', 'Sem nome')}</b>",
            subtitle_style
        )
        elements.append(report_name)
        elements.append(Spacer(1, SPACING_MEDIUM))

        # Report details
        body_style = self.styles["Body"]
        small_style = self.styles["Small"]

        # Description
        if report.get("description"):
            desc = Paragraph(
                f"<b>Descrição:</b> {report.get('description')}",
                body_style
            )
            elements.append(desc)
            elements.append(Spacer(1, SPACING_SMALL))

        # Dates
        date_info = []
        if report.get("start_date"):
            date_info.append(f"<b>Início:</b> {format_date_br(report['start_date'])}")
        if report.get("end_date"):
            date_info.append(f"<b>Fim:</b> {format_date_br(report['end_date'])}")

        if date_info:
            dates = Paragraph(" | ".join(date_info), small_style)
            elements.append(dates)
            elements.append(Spacer(1, SPACING_SMALL))

        # Status
        status = report.get("status", "draft")
        status_text = {
            "draft": "Rascunho",
            "completed": "Concluído",
            "archived": "Arquivado"
        }.get(status, status)

        status_color = {
            "draft": colors.HexColor("#6B7280"),
            "completed": colors.HexColor("#10B981"),
            "archived": colors.HexColor("#9CA3AF")
        }.get(status, colors.black)

        status_para = Paragraph(
            f"<b>Status:</b> <font color='{status_color.hexval()}'>{status_text}</font>",
            small_style
        )
        elements.append(status_para)
        elements.append(Spacer(1, SPACING_LARGE))

        return elements

    def _build_summary(
        self,
        report: Dict[str, Any],
        receipts: List[Dict[str, Any]]
    ) -> List:
        """Build summary section with totals."""
        elements = []

        heading_style = self.styles["Heading"]
        heading = Paragraph("<b>Resumo</b>", heading_style)
        elements.append(heading)
        elements.append(Spacer(1, SPACING_SMALL))

        # Summary table
        total_value = Decimal(str(report.get("total_value", 0)))
        receipt_count = len(receipts)

        summary_data = [
            ["Total de Recibos", str(receipt_count)],
            ["Valor Total", format_brl(total_value)],
        ]

        # Add target value if exists
        if report.get("target_value"):
            target_value = Decimal(str(report["target_value"]))
            percentage = (total_value / target_value * 100) if target_value > 0 else 0
            summary_data.append([
                "Meta",
                f"{format_brl(target_value)} ({percentage:.1f}%)"
            ])

        summary_table = Table(
            summary_data,
            colWidths=[8 * cm, 6 * cm],
            hAlign=TA_LEFT
        )

        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.white),
            ("TEXTCOLOR", (0, 0), (-1, -1), COLOR_TEXT),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 11),
            ("BOTTOMPADDING", (0, 0), (-1, -1), SPACING_SMALL),
            ("TOPPADDING", (0, 0), (-1, -1), SPACING_SMALL),
            ("GRID", (0, 0), (-1, -1), TABLE_BORDER_WIDTH, COLOR_BORDER),
        ]))

        elements.append(summary_table)
        elements.append(Spacer(1, SPACING_LARGE))

        return elements

    def _build_receipts_table(self, receipts: List[Dict[str, Any]]) -> List:
        """Build receipts table section."""
        elements = []

        if not receipts:
            body_style = self.styles["Body"]
            no_receipts = Paragraph(
                "<i>Nenhum recibo adicionado a este relatório.</i>",
                body_style
            )
            elements.append(no_receipts)
            return elements

        heading_style = self.styles["Heading"]
        heading = Paragraph("<b>Recibos</b>", heading_style)
        elements.append(heading)
        elements.append(Spacer(1, SPACING_SMALL))

        # Table header
        table_data = [[
            "Data",
            "Descrição",
            "Categoria",
            "Valor"
        ]]

        # Table rows
        for receipt in receipts:
            date = format_date_br(receipt.get("date", "")) if receipt.get("date") else "-"
            description = receipt.get("description", "-") or "-"
            category = receipt.get("category", "-") or "-"
            value = format_brl(Decimal(str(receipt.get("value", 0))))

            table_data.append([date, description, category, value])

        # Create table
        receipt_table = Table(
            table_data,
            colWidths=[3 * cm, 6 * cm, 3 * cm, 3 * cm],
            repeatRows=1
        )

        # Table style
        receipt_table.setStyle(TableStyle([
            # Header
            ("BACKGROUND", (0, 0), (-1, 0), TABLE_HEADER_BACKGROUND),
            ("TEXTCOLOR", (0, 0), (-1, 0), TABLE_HEADER_TEXT),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), SPACING_SMALL),
            ("TOPPADDING", (0, 0), (-1, 0), SPACING_SMALL),

            # Body
            ("BACKGROUND", (0, 1), (-1, -1), TABLE_ROW_BACKGROUND),
            ("TEXTCOLOR", (0, 1), (-1, -1), COLOR_TEXT),
            ("ALIGN", (0, 1), (0, -1), "LEFT"),  # Date
            ("ALIGN", (1, 1), (1, -1), "LEFT"),  # Description
            ("ALIGN", (2, 1), (2, -1), "LEFT"),  # Category
            ("ALIGN", (3, 1), (3, -1), "RIGHT"),  # Value
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 1), (-1, -1), SPACING_SMALL),
            ("TOPPADDING", (0, 1), (-1, -1), SPACING_SMALL),

            # Grid
            ("GRID", (0, 0), (-1, -1), TABLE_BORDER_WIDTH, TABLE_BORDER_COLOR),

            # Alternating row colors
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
                TABLE_ROW_BACKGROUND,
                TABLE_ALTERNATE_ROW_BACKGROUND
            ]),
        ]))

        elements.append(receipt_table)
        elements.append(Spacer(1, SPACING_LARGE))

        return elements

    def _build_footer(self) -> List:
        """Build PDF footer section."""
        elements = []

        footer_style = self.styles["Footer"]
        now = datetime.now()
        footer_text = f"Gerado em {format_datetime_br(now)} por RelatoRecibo"
        footer = Paragraph(footer_text, footer_style)
        elements.append(footer)

        return elements
