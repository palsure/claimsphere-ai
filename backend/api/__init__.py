"""API routes module"""
from fastapi import APIRouter
from .auth import router as auth_router
from .claims import router as claims_router
from .users import router as users_router
from .plans import router as plans_router
from .validation import router as validation_router
from .query import router as query_router
from .admin import router as admin_router

# Main API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(claims_router, prefix="/claims", tags=["Claims"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(plans_router, prefix="/plans", tags=["Plans"])
api_router.include_router(validation_router, prefix="/validation", tags=["Validation"])
api_router.include_router(query_router, prefix="/query", tags=["Natural Language Query"])
api_router.include_router(admin_router, prefix="/admin", tags=["Admin"])

