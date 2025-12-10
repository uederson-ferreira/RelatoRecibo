"""
PDF Generator Module

Main service for generating PDF reports.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from uuid import UUID
from typing import Optional, Dict, Any
from io import BytesIO
from supabase import Client
from loguru import logger

from app.repositories.report_repository import ReportRepository
from app.repositories.receipt_repository import ReceiptRepository
from app.repositories.user_repository import UserRepository
from app.services.pdf.templates.report_template import ReportPDFTemplate
from app.services.storage.uploader import StorageUploader
from app.core.exceptions.report import ReportNotFoundException, ReportAccessDeniedException
from app.core.exceptions.receipt import ReceiptNotFoundException


class PDFGenerator:
    """
    Service for generating PDF reports.

    Features:
    - Generate PDF from report data
    - Upload PDF to storage
    - Return download URL
    """

    def __init__(self, db: Client):
        """
        Initialize PDF generator.

        Args:
            db: Supabase client instance
        """
        self.db = db
        self.report_repo = ReportRepository(db)
        self.receipt_repo = ReceiptRepository(db)
        self.user_repo = UserRepository(db)
        self.storage_uploader = StorageUploader(db)
        self.template = ReportPDFTemplate()

    async def generate_report_pdf(
        self,
        report_id: UUID,
        user_id: UUID,
        upload_to_storage: bool = True
    ) -> Dict[str, Any]:
        """
        Generate PDF for a report.

        Args:
            report_id: Report UUID
            user_id: User UUID (for authorization)
            upload_to_storage: Whether to upload PDF to storage

        Returns:
            Dict with PDF data and optional storage URL

        Raises:
            ReportNotFoundException: If report not found
            ReportAccessDeniedException: If user doesn't own report
        """
        try:
            # Fetch report
            report = await self.report_repo.find_by_id_and_user(report_id, user_id)
            if not report:
                raise ReportNotFoundException(report_id=report_id)

            # Verify ownership
            if str(report["user_id"]) != str(user_id):
                raise ReportAccessDeniedException(report_id=report_id)

            # Fetch receipts
            receipts = await self.receipt_repo.find_by_report(
                report_id=report_id,
                user_id=user_id,
                limit=1000  # Get all receipts
            )

            # Get user name for header
            user = await self.user_repo.find_by_id(user_id)
            user_name = user.get("full_name") if user else None

            # Generate PDF
            logger.info(f"Generating PDF for report {report_id}")
            pdf_buffer = self.template.generate(
                report=report,
                receipts=receipts,
                user_name=user_name
            )

            # Read PDF bytes
            pdf_bytes = pdf_buffer.read()
            pdf_size = len(pdf_bytes)

            logger.info(f"PDF generated successfully: {pdf_size} bytes")

            result = {
                "pdf_bytes": pdf_bytes,
                "pdf_size": pdf_size,
                "report_id": str(report_id),
                "report_name": report.get("name", "Relatório"),
                "receipt_count": len(receipts),
            }

            # Upload to storage if requested
            if upload_to_storage:
                logger.info(f"Uploading PDF to storage for report {report_id}")
                pdf_url = await self.storage_uploader.upload_pdf(
                    pdf_data=pdf_bytes,
                    user_id=user_id,
                    report_id=report_id
                )
                result["pdf_url"] = pdf_url
                logger.info(f"PDF uploaded successfully: {pdf_url}")

            return result

        except (ReportNotFoundException, ReportAccessDeniedException):
            raise
        except Exception as e:
            logger.error(f"Error generating PDF for report {report_id}: {e}")
            raise

    async def generate_pdf_bytes_only(
        self,
        report_id: UUID,
        user_id: UUID
    ) -> bytes:
        """
        Generate PDF and return only bytes (no storage upload).

        Useful for direct download endpoints.

        Args:
            report_id: Report UUID
            user_id: User UUID

        Returns:
            PDF bytes
        """
        result = await self.generate_report_pdf(
            report_id=report_id,
            user_id=user_id,
            upload_to_storage=False
        )
        return result["pdf_bytes"]
