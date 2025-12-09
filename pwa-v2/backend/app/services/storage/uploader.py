"""
Storage Uploader Module

Handles file uploads to Supabase Storage.
Manages receipts, thumbnails, and PDFs.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

import io
from uuid import UUID
from typing import Optional, Tuple
from pathlib import Path
from PIL import Image
from supabase import Client
from loguru import logger

from app.utils.constants import (
    STORAGE_BUCKET_RECEIPTS,
    STORAGE_PATH_ORIGINALS,
    STORAGE_PATH_THUMBNAILS,
    STORAGE_PATH_PDFS,
    THUMBNAIL_SIZE,
    MAX_IMAGE_WIDTH,
    MAX_IMAGE_HEIGHT
)
from app.core.exceptions.receipt import StorageUploadException


class StorageUploader:
    """
    Handles file uploads to Supabase Storage.

    Features:
    - Upload original images
    - Generate and upload thumbnails
    - Upload PDFs
    - Generate signed URLs
    - Delete files
    """

    def __init__(self, client: Client):
        """
        Initialize the storage uploader.

        Args:
            client: Supabase client instance
        """
        self.client = client
        self.bucket = STORAGE_BUCKET_RECEIPTS

    def _generate_file_path(
        self,
        user_id: UUID,
        receipt_id: UUID,
        file_type: str,
        extension: str
    ) -> str:
        """
        Generate storage path for a file.

        Args:
            user_id: User UUID
            receipt_id: Receipt UUID
            file_type: Type of file (originals, thumbnails, pdfs)
            extension: File extension (jpg, png, pdf)

        Returns:
            Storage path (e.g., "originals/user-id/receipt-id.jpg")
        """
        return f"{file_type}/{user_id}/{receipt_id}.{extension}"

    async def upload_image(
        self,
        image_data: bytes,
        user_id: UUID,
        receipt_id: UUID,
        content_type: str = "image/jpeg"
    ) -> Tuple[str, str]:
        """
        Upload original image and generate thumbnail.

        Args:
            image_data: Image binary data
            user_id: User UUID
            receipt_id: Receipt UUID
            content_type: MIME type

        Returns:
            Tuple of (original_url, thumbnail_url)

        Raises:
            StorageUploadException: If upload fails
        """
        try:
            # Determine extension from content type
            extension_map = {
                "image/jpeg": "jpg",
                "image/jpg": "jpg",
                "image/png": "png",
                "image/webp": "webp"
            }
            extension = extension_map.get(content_type, "jpg")

            # Upload original image
            original_path = self._generate_file_path(
                user_id, receipt_id, STORAGE_PATH_ORIGINALS, extension
            )

            original_response = self.client.storage.from_(self.bucket).upload(
                path=original_path,
                file=image_data,
                file_options={"content-type": content_type}
            )

            if not original_response:
                raise StorageUploadException(
                    details={"path": original_path, "type": "original"}
                )

            # Generate and upload thumbnail
            thumbnail_data = await self._generate_thumbnail(image_data)
            thumbnail_path = self._generate_file_path(
                user_id, receipt_id, STORAGE_PATH_THUMBNAILS, extension
            )

            thumbnail_response = self.client.storage.from_(self.bucket).upload(
                path=thumbnail_path,
                file=thumbnail_data,
                file_options={"content-type": content_type}
            )

            if not thumbnail_response:
                raise StorageUploadException(
                    details={"path": thumbnail_path, "type": "thumbnail"}
                )

            # Generate signed URLs (valid for 1 year)
            original_url = self.client.storage.from_(self.bucket).create_signed_url(
                path=original_path,
                expires_in=31536000  # 1 year in seconds
            )

            thumbnail_url = self.client.storage.from_(self.bucket).create_signed_url(
                path=thumbnail_path,
                expires_in=31536000
            )

            logger.info(f"Image uploaded successfully: {receipt_id}")

            return original_url["signedURL"], thumbnail_url["signedURL"]

        except Exception as e:
            logger.error(f"Error uploading image: {e}")
            raise StorageUploadException(
                details={"receipt_id": str(receipt_id), "error": str(e)}
            )

    async def _generate_thumbnail(self, image_data: bytes) -> bytes:
        """
        Generate thumbnail from image data.

        Args:
            image_data: Original image binary data

        Returns:
            Thumbnail binary data
        """
        try:
            # Open image
            image = Image.open(io.BytesIO(image_data))

            # Convert RGBA to RGB if necessary
            if image.mode == "RGBA":
                # Create white background
                background = Image.new("RGB", image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])  # Use alpha channel as mask
                image = background
            elif image.mode != "RGB":
                image = image.convert("RGB")

            # Resize maintaining aspect ratio
            image.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)

            # Save to bytes
            output = io.BytesIO()
            image.save(output, format="JPEG", quality=85, optimize=True)
            output.seek(0)

            return output.read()

        except Exception as e:
            logger.error(f"Error generating thumbnail: {e}")
            # Return original if thumbnail generation fails
            return image_data

    async def upload_pdf(
        self,
        pdf_data: bytes,
        user_id: UUID,
        report_id: UUID
    ) -> str:
        """
        Upload PDF report.

        Args:
            pdf_data: PDF binary data
            user_id: User UUID
            report_id: Report UUID

        Returns:
            Signed URL to PDF

        Raises:
            StorageUploadException: If upload fails
        """
        try:
            pdf_path = self._generate_file_path(
                user_id, report_id, STORAGE_PATH_PDFS, "pdf"
            )

            response = self.client.storage.from_(self.bucket).upload(
                path=pdf_path,
                file=pdf_data,
                file_options={"content-type": "application/pdf"}
            )

            if not response:
                raise StorageUploadException(
                    details={"path": pdf_path, "type": "pdf"}
                )

            # Generate signed URL (valid for 1 year)
            signed_url = self.client.storage.from_(self.bucket).create_signed_url(
                path=pdf_path,
                expires_in=31536000
            )

            logger.info(f"PDF uploaded successfully: {report_id}")

            return signed_url["signedURL"]

        except Exception as e:
            logger.error(f"Error uploading PDF: {e}")
            raise StorageUploadException(
                details={"report_id": str(report_id), "error": str(e)}
            )

    async def delete_image(self, user_id: UUID, receipt_id: UUID) -> bool:
        """
        Delete receipt image and thumbnail.

        Args:
            user_id: User UUID
            receipt_id: Receipt UUID

        Returns:
            True if successful
        """
        try:
            # Try all possible extensions
            extensions = ["jpg", "jpeg", "png", "webp"]
            deleted_count = 0

            for extension in extensions:
                # Delete original
                original_path = self._generate_file_path(
                    user_id, receipt_id, STORAGE_PATH_ORIGINALS, extension
                )

                try:
                    self.client.storage.from_(self.bucket).remove([original_path])
                    deleted_count += 1
                except:
                    pass  # File might not exist with this extension

                # Delete thumbnail
                thumbnail_path = self._generate_file_path(
                    user_id, receipt_id, STORAGE_PATH_THUMBNAILS, extension
                )

                try:
                    self.client.storage.from_(self.bucket).remove([thumbnail_path])
                    deleted_count += 1
                except:
                    pass

            logger.info(f"Deleted {deleted_count} files for receipt {receipt_id}")
            return deleted_count > 0

        except Exception as e:
            logger.error(f"Error deleting image: {e}")
            return False

    async def delete_pdf(self, user_id: UUID, report_id: UUID) -> bool:
        """
        Delete PDF report.

        Args:
            user_id: User UUID
            report_id: Report UUID

        Returns:
            True if successful
        """
        try:
            pdf_path = self._generate_file_path(
                user_id, report_id, STORAGE_PATH_PDFS, "pdf"
            )

            self.client.storage.from_(self.bucket).remove([pdf_path])

            logger.info(f"Deleted PDF for report {report_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting PDF: {e}")
            return False
