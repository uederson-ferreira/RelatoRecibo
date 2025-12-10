"""
Authentication Endpoints Module

Handles user authentication: signup, login, logout.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

import asyncio
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from loguru import logger

from app.dependencies import get_db
from app.models.user import UserCreate, UserLogin, TokenResponse, UserResponse
from app.repositories.user_repository import UserRepository
from app.core.security.password import hash_password, verify_password
from app.core.security.jwt import create_access_token
from app.core.exceptions.auth import (
    InvalidCredentialsException,
    UserAlreadyExistsException
)
from app.config import settings


router = APIRouter()


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    db: Client = Depends(get_db)
):
    """
    Create a new user account.

    - **email**: Valid email address (unique)
    - **password**: Strong password (min 8 chars, uppercase, lowercase, digit)
    - **full_name**: User's full name (optional)

    Returns:
    - JWT access token
    - User information

    Raises:
    - 400: Email already exists
    - 422: Validation error (weak password, invalid email)
    """
    try:
        user_repo = UserRepository(db)

        # Check if email already exists
        if await user_repo.email_exists(user_data.email):
            raise UserAlreadyExistsException(
                details={"email": user_data.email}
            )

        # Create user with Supabase Auth
        auth_response = db.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
            "options": {
                "data": {
                    "full_name": user_data.full_name
                }
            }
        })

        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )

        user_id_str = auth_response.user.id
        user_id = UUID(user_id_str)  # Convert to UUID for repository methods

        # Note: The trigger handle_new_user() should auto-create the profile
        # Wait a moment for the trigger to execute, then verify profile exists
        await asyncio.sleep(0.5)  # Small delay for trigger execution

        # Verify profile was created by trigger, or create it if it doesn't exist
        user_profile = await user_repo.find_by_id(user_id)
        if not user_profile:
            # Profile not created by trigger, create it manually
            logger.warning(f"Profile not auto-created for user {user_id}, creating manually")
            profile_data = {
                "id": str(user_id),  # Supabase expects string UUID
                "email": user_data.email,
                "full_name": user_data.full_name
            }
            try:
                await user_repo.create(profile_data)
            except Exception as profile_error:
                logger.error(f"Error creating profile for user {user_id}: {profile_error}")
                # Try to clean up auth user if profile creation fails
                try:
                    db.auth.admin.delete_user(user_id_str)  # Use string UUID for Supabase admin API
                except Exception as cleanup_error:
                    logger.warning(f"Failed to cleanup auth user {user_id_str}: {cleanup_error}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to create user profile: {str(profile_error)}"
                )
        else:
            # Profile exists, update full_name if it wasn't set by trigger
            if not user_profile.get('full_name') and user_data.full_name:
                await user_repo.update_profile(user_id, {"full_name": user_data.full_name})
                user_profile = await user_repo.find_by_id(user_id)

        # Ensure profile exists
        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User profile not found after creation"
            )

        # Create access token
        access_token = create_access_token(
            user_id=user_id,  # Use UUID object
            email=user_data.email
        )

        logger.info(f"User created successfully: {user_data.email}")

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse(**user_profile)
        )

    except UserAlreadyExistsException:
        raise
    except HTTPException:
        # Re-raise HTTP exceptions (already formatted)
        raise
    except Exception as e:
        logger.error(f"Error during signup: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during signup: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: Client = Depends(get_db)
):
    """
    Authenticate user and return JWT token.

    - **email**: User email
    - **password**: User password

    Returns:
    - JWT access token
    - User information

    Raises:
    - 401: Invalid credentials
    """
    try:
        # Authenticate with Supabase Auth
        auth_response = db.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })

        if not auth_response.user:
            raise InvalidCredentialsException()

        user_id = auth_response.user.id

        # Fetch user profile
        user_repo = UserRepository(db)
        user_profile = await user_repo.find_by_id(user_id)

        if not user_profile:
            raise InvalidCredentialsException()

        # Create access token
        access_token = create_access_token(
            user_id=user_id,
            email=credentials.email
        )

        logger.info(f"User logged in successfully: {credentials.email}")

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse(**user_profile)
        )

    except InvalidCredentialsException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise InvalidCredentialsException()


@router.post("/logout")
async def logout():
    """
    Logout user (client-side token removal).

    Note:
    - JWT tokens are stateless
    - Client should remove token from storage
    - Token will expire automatically after expiration time

    Returns:
    - Success message
    """
    logger.info("User logout request")

    return {
        "success": True,
        "message": "Logged out successfully. Please remove the token from client storage."
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    # TODO: Use get_current_user_id dependency when implemented
    db: Client = Depends(get_db)
):
    """
    Get current authenticated user information.

    Requires:
    - Valid JWT token in Authorization header

    Returns:
    - User profile information

    Raises:
    - 401: Invalid or missing token
    """
    # TODO: Implement this endpoint with proper JWT validation
    # For now, return a placeholder response
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint not yet implemented. Need to update dependencies.py first."
    )
