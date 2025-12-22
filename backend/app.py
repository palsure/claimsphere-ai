"""
FastAPI backend for ClaimSphere AI - Automated Claim Processing System
"""
import os
from typing import Optional, List, Dict, Any

import uuid
import gc
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, File, UploadFile
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
    allow_origins=[frontend_url, "http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003", "http://127.0.0.1:3000", "http://127.0.0.1:3001", "http://127.0.0.1:3002", "http://127.0.0.1:3003"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services - OCR is lazy-loaded to save memory
# OCR will be initialized on first use, not at startup
# Check if OCR should be disabled (e.g., on Render free tier)
DISABLE_OCR = os.getenv("DISABLE_OCR", "").lower() in ("true", "1", "yes")

if DISABLE_OCR:
    print("=" * 60)
    print("OCR IS DISABLED")
    print("Reason: DISABLE_OCR environment variable is set")
    print("Service will process files using ERNIE AI without OCR")
    print("=" * 60)
    ocr_processor = None
    ocr_initialized = True  # Mark as initialized to prevent attempts
else:
    ocr_processor = None  # Will be initialized lazily when needed
    ocr_initialized = False


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
    import sys
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "ocr_initialized": ocr_initialized,
        "service": "claim-processing-api"
    }


@app.post("/api/claims/upload")
async def upload_claim_document(
    file: UploadFile = File(...),
    process_with_ai: bool = True
):
    """
    Upload and process a claim document (form, receipt, medical record, etc.)
    
    Args:
        file: Claim document image or PDF file
        process_with_ai: Whether to use ERNIE for extraction and validation
        
    Returns:
        Processed claim information
    """
    print(f"[UPLOAD] Starting upload - File: {file.filename}, Process with AI: {process_with_ai}")
    try:
        # Read file content with size limit (10MB max)
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        print(f"[UPLOAD] Reading file bytes...")
        file_bytes = await file.read()
        print(f"[UPLOAD] File size: {len(file_bytes) / (1024*1024):.2f}MB")
        
        if len(file_bytes) > MAX_FILE_SIZE:
            print(f"[UPLOAD] File too large: {len(file_bytes) / (1024*1024):.2f}MB")
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE / (1024*1024):.1f}MB"
            )
        
        file_type = "pdf" if file.filename and file.filename.endswith(".pdf") else "image"
        print(f"[UPLOAD] File type: {file_type}")
        
        # Lazy-load OCR processor to save memory
        global ocr_processor, ocr_initialized
        
        # Check if OCR is disabled
        if DISABLE_OCR:
            print("[UPLOAD] OCR is disabled via DISABLE_OCR environment variable")
            ocr_result = {
                'text': f'OCR disabled on this server. File: {file.filename}',
                'text_lines': [],
                'layout': [],
                'language': 'unknown',
                'error': 'OCR disabled to save memory'
            }
        elif not ocr_initialized:
            print("[UPLOAD] Initializing OCR processor (first time)...")
            try:
                ocr_processor = OCRProcessor(lang='en')
                ocr_initialized = True
                if ocr_processor.ocr is None:
                    print("[UPLOAD] WARNING: PaddleOCR is not available. OCR features will not work.")
                else:
                    print("[UPLOAD] OCR processor initialized successfully")
            except Exception as e:
                print(f"[UPLOAD] WARNING: Failed to initialize OCR processor: {e}")
                import traceback
                traceback.print_exc()
                ocr_processor = None
                ocr_initialized = True  # Mark as attempted to avoid retrying
        
        # Process with OCR if not disabled and initialized
        if not DISABLE_OCR and ocr_processor is not None and ocr_processor.ocr is not None:
            # Process with OCR - wrap in try/except to handle timeouts
            print("[UPLOAD] Starting OCR processing...")
            try:
                import asyncio
                # Run OCR in executor to avoid blocking
                loop = asyncio.get_event_loop()
                print("[UPLOAD] Running OCR in executor...")
                ocr_result = await loop.run_in_executor(
                    None, 
                    ocr_processor.process_bytes, 
                    file_bytes, 
                    file_type
                )
                print(f"[UPLOAD] OCR completed - Extracted {len(ocr_result.get('text', ''))} characters")
            except Exception as ocr_error:
                print(f"[UPLOAD] OCR processing error: {ocr_error}")
                import traceback
                traceback.print_exc()
                ocr_result = {
                    'text': f'OCR processing failed: {str(ocr_error)}',
                    'text_lines': [],
                    'layout': [],
                    'language': 'unknown',
                    'error': str(ocr_error)
                }
        elif DISABLE_OCR:
            # Already set above in the first if block
            pass
        else:
            # OCR not available
            print("[UPLOAD] OCR not available, skipping OCR processing")
            ocr_result = {
                'text': f'OCR not available. File: {file.filename}',
                'text_lines': [],
                'layout': [],
                'language': 'unknown',
                'error': 'OCR processor not initialized'
            }
        
        # Continue processing even if OCR had errors (non-critical)
        # Only log the error but don't fail the request
        if "error" in ocr_result:
            print(f"[UPLOAD] OCR warning: {ocr_result['error']}")
            # Continue with whatever text was extracted (even if empty)
        
        # Extract claim information
        print(f"[UPLOAD] Extracting claim information (AI: {process_with_ai})...")
        if process_with_ai:
            claim_data = ernie_service.extract_claim_info(
                ocr_result.get("text", ""),
                ocr_result.get("layout", [])
            )
        else:
            # Basic extraction without AI
            claim_data = {
                "claimant_name": "Unknown",
                "date_of_incident": datetime.now().isoformat()[:10],
                "total_amount": 0.0,
                "currency": "USD",
                "claim_type": "other",
                "items": [],
                "description": "Basic extraction only"
            }
        
        # Generate claim number
        claim_number = f"CLM-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Parse date
        try:
            date_of_incident = datetime.fromisoformat(claim_data.get("date_of_incident", datetime.now().isoformat()[:10]))
        except:
            date_of_incident = datetime.now()
        
        # Create claim object
        claim = Claim(
            id=str(uuid.uuid4()),
            claim_number=claim_number,
            claimant_name=claim_data.get("claimant_name", "Unknown"),
            claim_type=ClaimType(claim_data.get("claim_type", "other")),
            date_of_incident=date_of_incident,
            date_submitted=datetime.now(),
            total_amount=float(claim_data.get("total_amount", 0.0)),
            currency=claim_data.get("currency", "USD"),
            items=claim_data.get("items", []),
            description=claim_data.get("description"),
            language=ocr_result.get("language", "unknown"),
            status=ClaimStatus.PENDING,
            supporting_documents=[file.filename] if file.filename else []
        )
        
        # Validate claim
        validation_errors = claim_processor.validate_claim(claim)
        claim.validation_errors = validation_errors
        
        # AI validation
        if process_with_ai:
            ai_validation = ernie_service.validate_claim_with_ai(claim_data)
            if not ai_validation.get("is_valid", True):
                validation_errors.extend(ai_validation.get("validation_errors", []))
                if ai_validation.get("requires_manual_review", False):
                    claim.status = ClaimStatus.REQUIRES_INFO
        
        # Check for duplicates and anomalies
        duplicates = claim_processor.detect_duplicates(claim)
        anomalies = claim_processor.detect_anomalies(claim)
        
        if duplicates:
            claim.is_duplicate = True
            claim.description = (claim.description or "") + f" | Potential duplicate of {len(duplicates)} claim(s)"
        
        # Add to processor and database
        claim_processor.add_claim(claim)
        claims_db.append(claim)
        
        # Limit claims_db size to prevent memory growth (keep last 1000 claims)
        MAX_CLAIMS_IN_MEMORY = 1000
        if len(claims_db) > MAX_CLAIMS_IN_MEMORY:
            claims_db[:] = claims_db[-MAX_CLAIMS_IN_MEMORY:]
        
        # Clear file_bytes from memory after processing
        print("[UPLOAD] Cleaning up memory...")
        del file_bytes
        # Force garbage collection to free memory
        gc.collect()
        
        print(f"[UPLOAD] Successfully processed claim {claim.id}")
        return {
            "claim": claim.dict(),
            "ocr_text": ocr_result.get("text", "")[:1000] if ocr_result.get("text") else "",  # Limit OCR text in response
            "duplicates_found": len(duplicates),
            "anomalies": anomalies,
            "validation_errors": validation_errors,
            "processing_info": {
                "language_detected": ocr_result.get("language"),
                "text_lines_extracted": len(ocr_result.get("text_lines", []))
            }
        }
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[UPLOAD] ERROR processing file: {error_trace}")
        # Clean up file_bytes if it exists
        if 'file_bytes' in locals():
            try:
                del file_bytes
                gc.collect()
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.get("/api/claims")
async def get_claims(
    claim_type: Optional[str] = None,
    status: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = 100
):
    """
    Get list of claims with optional filters
    
    Args:
        claim_type: Filter by claim type
        status: Filter by status
        date_from: Start date (YYYY-MM-DD)
        date_to: End date (YYYY-MM-DD)
        limit: Maximum number of results
        
    Returns:
        List of claims
    """
    filtered_claims = claims_db
    
    # Apply filters
    if claim_type:
        filtered_claims = [c for c in filtered_claims if c.claim_type and c.claim_type.value == claim_type]
    
    if status:
        filtered_claims = [c for c in filtered_claims if c.status and c.status.value == status]
    
    if date_from:
        date_from_obj = datetime.fromisoformat(date_from)
        filtered_claims = [c for c in filtered_claims if c.date_submitted >= date_from_obj]
    
    if date_to:
        date_to_obj = datetime.fromisoformat(date_to)
        filtered_claims = [c for c in filtered_claims if c.date_submitted <= date_to_obj]
    
    # Sort by date (newest first) and limit
    filtered_claims.sort(key=lambda x: x.date_submitted, reverse=True)
    filtered_claims = filtered_claims[:limit]
    

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
    import sys
    print("=" * 60)
    print("Starting Automated Claim Processing Agent API")
    print(f"Python version: {sys.version}")
    print(f"Host: 0.0.0.0")
    print(f"Port: {os.getenv('PORT', '8000')}")
    print("OCR: Lazy-loaded (will initialize on first upload)")
    print("Health check: /health")
    print("=" * 60)
    
    port = int(os.getenv("PORT", 8000))

    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=port,
        reload=debug
    )

    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

