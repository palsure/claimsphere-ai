"""
FastAPI backend for ClaimSphere AI - Automated Claim Processing System
"""
import os
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database and initialize
from backend.database.config import engine, Base, SessionLocal, init_db
from backend.database.models import Role, RoleType
from backend.auth.service import AuthService

# Import API routes
from backend.api import api_router


def seed_demo_users(db):
    """Seed demo users for testing"""
    demo_users = [
        {
            "email": "admin@example.com",
            "password": "password123",
            "first_name": "Admin",
            "last_name": "User",
            "roles": [RoleType.ADMIN]
        },
        {
            "email": "agent@example.com",
            "password": "password123",
            "first_name": "Agent",
            "last_name": "Smith",
            "roles": [RoleType.AGENT]
        },
        {
            "email": "user@example.com",
            "password": "password123",
            "first_name": "John",
            "last_name": "Doe",
            "roles": [RoleType.USER]
        }
    ]
    
    for user_data in demo_users:
        try:
            existing = AuthService.get_user_by_email(db, user_data["email"])
            if not existing:
                AuthService.create_user(
                    db,
                    email=user_data["email"],
                    password=user_data["password"],
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    roles=user_data["roles"]
                )
                print(f"  Created demo user: {user_data['email']}")
            else:
                print(f"  Demo user exists: {user_data['email']}")
        except Exception as e:
            print(f"  Error creating {user_data['email']}: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("Initializing database...")
    init_db()
    
    # Initialize default roles and demo users
    db = SessionLocal()
    try:
        AuthService.init_default_roles(db)
        print("Default roles initialized")
        
        print("Seeding demo users...")
        seed_demo_users(db)
        print("Demo users seeded")
    finally:
        db.close()
    
    yield
    
    # Shutdown
    print("Application shutting down...")


# Create FastAPI app
app = FastAPI(
    title="ClaimSphere AI API",
    description="AI-powered claim processing system with RBAC, auto-approval, and natural language queries",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    import traceback
    error_trace = traceback.format_exc()
    print(f"Unhandled exception: {error_trace}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "type": type(exc).__name__
        }
    )


# Include API routes
app.include_router(api_router, prefix="/api")


# Root endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ClaimSphere AI API",
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": {
            "auth": "/api/auth",
            "claims": "/api/claims",
            "users": "/api/users",
            "plans": "/api/plans",
            "validation": "/api/validation",
            "query": "/api/query",
            "admin": "/api/admin"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }


# Legacy endpoints for backward compatibility
@app.get("/api/claims/legacy")
async def legacy_claims_endpoint():
    """Legacy endpoint redirect notice"""
    return {
        "message": "This endpoint has been updated. Please use /api/claims with authentication.",
        "docs": "/docs"
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=port,
        reload=debug
    )
