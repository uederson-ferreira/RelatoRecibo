"""
API v1 Router Module

Aggregates all v1 API endpoints.
Main router that includes all sub-routers.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from fastapi import APIRouter

# Import sub-routers
from app.api.v1.auth import endpoints as auth_endpoints
from app.api.v1.reports import endpoints as reports_endpoints
from app.api.v1.receipts import endpoints as receipts_endpoints
# from app.api.v1.profile import endpoints as profile_endpoints


# Main API v1 router
api_router = APIRouter()

# Include auth endpoints
api_router.include_router(
    auth_endpoints.router,
    prefix="/auth",
    tags=["Authentication"]
)

# Include reports endpoints
api_router.include_router(
    reports_endpoints.router,
    prefix="/reports",
    tags=["Reports"]
)

# Include receipts endpoints
api_router.include_router(
    receipts_endpoints.router,
    prefix="/receipts",
    tags=["Receipts"]
)

# Include profile endpoints
# api_router.include_router(
#     profile_endpoints.router,
#     prefix="/profile",
#     tags=["Profile"]
# )
