"""
Profile Endpoints Module

Handles user profile operations.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from supabase import Client
from loguru import logger

from app.dependencies import get_db, get_current_user_id
from app.api.v1.profile.schemas import (
    ProfileUpdate,
    ProfileResponse,
    UserStatsResponse
)
from app.repositories.user_repository import UserRepository
from app.services.storage.uploader import StorageUploader
from app.core.exceptions.auth import UserNotFoundException
from app.models.base import SuccessResponse


router = APIRouter()


@router.get("", response_model=ProfileResponse)
async def get_profile(
    db: Client = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get current user profile.

    Returns:
    - User profile information

    Raises:
    - 401: Unauthorized (missing or invalid token)
    - 404: User not found
    """
    try:
        repo = UserRepository(db)

        # Fetch user profile
        user = await repo.find_by_id(UUID(user_id))

        if not user:
            raise UserNotFoundException(user_id=user_id)

        logger.info(f"Profile retrieved for user {user_id}")

        return ProfileResponse(**user)

    except UserNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error getting profile for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get profile"
        )


@router.put("", response_model=ProfileResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    db: Client = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Update user profile.

    Body (all optional):
    - **full_name**: New full name
    - **email**: New email (must be unique)

    Returns:
    - Updated profile

    Raises:
    - 401: Unauthorized (missing or invalid token)
    - 404: User not found
    - 409: Email already exists (if changing email)
    - 422: Validation error
    """
    try:
        repo = UserRepository(db)

        # Check if user exists
        existing = await repo.find_by_id(UUID(user_id))
        if not existing:
            raise UserNotFoundException(user_id=user_id)

        # Check if email is being changed and if it's already taken
        update_dict = profile_data.model_dump(exclude_unset=True)
        if "email" in update_dict and update_dict["email"] != existing.get("email"):
            email_exists = await repo.email_exists(update_dict["email"])
            if email_exists:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already exists"
                )

        # Update profile
        updated = await repo.update_profile(
            user_id=UUID(user_id),
            profile_data=update_dict
        )

        if not updated:
            raise UserNotFoundException(user_id=user_id)

        logger.info(f"Profile updated for user {user_id}")

        return ProfileResponse(**updated)

    except (UserNotFoundException, HTTPException):
        raise
    except Exception as e:
        logger.error(f"Error updating profile for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.post("/avatar", response_model=ProfileResponse)
async def upload_avatar(
    file: UploadFile = File(..., description="Avatar image file"),
    db: Client = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Upload user avatar image.

    Body:
    - **file**: Image file (jpg, png, webp, max 5MB)

    Returns:
    - Updated profile with avatar_url

    Raises:
    - 401: Unauthorized (missing or invalid token)
    - 400: Invalid file type or size
    - 404: User not found
    """
    try:
        from app.utils.validators.file import validate_image_file
        from app.utils.constants import MAX_FILE_SIZE

        # Validate file
        file_content = await file.read()
        await file.seek(0)  # Reset file pointer

        validate_image_file(
            filename=file.filename or "avatar",
            content_type=file.content_type or "",
            file_size=len(file_content)
        )

        # Upload to storage
        storage_uploader = StorageUploader(db)

        # Use a temporary receipt_id for avatar (we'll use user_id as receipt_id)
        avatar_url, _ = await storage_uploader.upload_image(
            image_data=file_content,
            user_id=UUID(user_id),
            receipt_id=UUID(user_id),  # Use user_id as receipt_id for avatars
            content_type=file.content_type or "image/jpeg"
        )

        # Update profile with avatar URL
        repo = UserRepository(db)
        updated = await repo.update_avatar(
            user_id=UUID(user_id),
            avatar_url=avatar_url
        )

        if not updated:
            raise UserNotFoundException(user_id=user_id)

        logger.info(f"Avatar uploaded for user {user_id}")

        return ProfileResponse(**updated)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except UserNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error uploading avatar for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload avatar"
        )


@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(
    db: Client = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get user statistics.

    Returns:
    - User statistics (total reports, receipts, value, etc.)

    Raises:
    - 401: Unauthorized (missing or invalid token)
    """
    try:
        repo = UserRepository(db)

        # Get stats
        stats = await repo.get_stats(UUID(user_id))

        logger.info(f"Stats retrieved for user {user_id}")

        return UserStatsResponse(**stats)

    except Exception as e:
        logger.error(f"Error getting stats for user {user_id}: {e}")
        # Return empty stats on error
        return UserStatsResponse(
            total_reports=0,
            total_receipts=0,
            total_value=0.0,
            reports_by_status={}
        )
