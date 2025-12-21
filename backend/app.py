"""
FastAPI backend for Automated Claim Processing Agent
"""
import os
import sys
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.ocr_processor import OCRProcessor
from backend.ernie_service import ErnieService
from backend.claim_processor import ClaimProcessor
from backend.models.claim import Claim, ClaimType, ClaimStatus, ClaimQuery, ClaimAnalytics

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Automated Claim Processing Agent API",
    description="AI-powered claim processing system using PaddleOCR and ERNIE",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
ocr_processor = OCRProcessor(lang='en')  # Use English for EOB and insurance documents
ernie_service = ErnieService()
claim_processor = ClaimProcessor()

# In-memory storage (replace with database in production)
claims_db: List[Claim] = []


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Automated Claim Processing Agent API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "upload": "/api/claims/upload",
            "claims": "/api/claims",
            "analytics": "/api/claims/analytics",
            "query": "/api/claims/query"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


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
    try:
        # Read file content
        file_bytes = await file.read()
        file_type = "pdf" if file.filename and file.filename.endswith(".pdf") else "image"
        
        # Process with OCR
        ocr_result = ocr_processor.process_bytes(file_bytes, file_type)
        
        if "error" in ocr_result:
            error_msg = ocr_result['error']
            # If it's a poppler error, provide helpful message but don't block image uploads
            if 'poppler' in error_msg.lower() or 'page count' in error_msg.lower():
                raise HTTPException(
                    status_code=400, 
                    detail=f"PDF processing requires poppler. Please install it with: brew install poppler. Alternatively, you can upload images (PNG, JPG) instead of PDFs. Error: {error_msg}"
                )
            raise HTTPException(status_code=400, detail=f"OCR processing failed: {error_msg}")
        
        # Extract claim information
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
        
        return {
            "claim": claim.dict(),
            "ocr_text": ocr_result.get("text", ""),
            "duplicates_found": len(duplicates),
            "anomalies": anomalies,
            "validation_errors": validation_errors,
            "processing_info": {
                "language_detected": ocr_result.get("language"),
                "text_lines_extracted": len(ocr_result.get("text_lines", []))
            }
        }
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error processing file: {error_trace}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)} - Traceback: {error_trace}")


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
        "claims": [claim.dict() for claim in filtered_claims],
        "total": len(filtered_claims),
        "filters": {
            "claim_type": claim_type,
            "status": status,
            "date_from": date_from,
            "date_to": date_to
        }
    }


@app.get("/api/claims/analytics")
async def get_analytics(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
):
    """
    Get claim analytics
    
    Args:
        date_from: Start date (YYYY-MM-DD)
        date_to: End date (YYYY-MM-DD)
        
    Returns:
        Analytics summary
    """
    date_from_obj = datetime.fromisoformat(date_from) if date_from else None
    date_to_obj = datetime.fromisoformat(date_to) if date_to else None
    
    analytics = claim_processor.generate_analytics(date_from_obj, date_to_obj)
    return analytics.dict()


@app.get("/api/claims/{claim_id}")
async def get_claim(claim_id: str):
    """Get a specific claim by ID"""
    claim = next((c for c in claims_db if c.id == claim_id), None)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim.dict()


class StatusUpdateRequest(BaseModel):
    status: str
    reviewer_notes: Optional[str] = None
    approved_amount: Optional[float] = None


@app.put("/api/claims/{claim_id}/status")
async def update_claim_status(
    claim_id: str,
    request: StatusUpdateRequest
):
    """Update claim status (approve, reject, etc.)"""
    claim = next((c for c in claims_db if c.id == claim_id), None)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    try:
        claim.status = ClaimStatus(request.status)
        claim.updated_at = datetime.now()
        
        if request.reviewer_notes:
            claim.reviewer_notes = request.reviewer_notes
        
        if request.status == "approved" and request.approved_amount is not None:
            claim.approved_amount = request.approved_amount
        elif request.status == "approved":
            claim.approved_amount = claim.total_amount
        
        if request.status == "rejected" and request.reviewer_notes:
            claim.rejection_reason = request.reviewer_notes
        
        return {"message": "Claim status updated", "claim": claim.dict()}
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {request.status}")


@app.delete("/api/claims/{claim_id}")
async def delete_claim(claim_id: str):
    """Delete a claim"""
    global claims_db
    claim = next((c for c in claims_db if c.id == claim_id), None)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    claims_db = [c for c in claims_db if c.id != claim_id]
    return {"message": "Claim deleted", "id": claim_id}


@app.post("/api/claims/query")
async def query_claims(query: ClaimQuery):
    """
    Answer natural language questions about claims
    
    Args:
        query: Natural language query
        
    Returns:
        Answer to the query
    """
    # Get relevant claims for context
    filtered_claims = claims_db
    
    if query.date_from:
        filtered_claims = [c for c in filtered_claims if c.date_submitted >= query.date_from]
    if query.date_to:
        filtered_claims = [c for c in filtered_claims if c.date_submitted <= query.date_to]
    if query.claim_type:
        filtered_claims = [c for c in filtered_claims if c.claim_type == query.claim_type]
    if query.status:
        filtered_claims = [c for c in filtered_claims if c.status == query.status]
    
    # Convert to dict for ERNIE
    claims_context = [claim.dict() for claim in filtered_claims]
    
    # Get answer from ERNIE
    answer = ernie_service.answer_claim_query(query.query, claims_context)
    
    return {
        "query": query.query,
        "answer": answer,
        "claims_analyzed": len(claims_context)
    }


@app.post("/api/claims/{claim_id}/categorize")
async def recategorize_claim(claim_id: str):
    """Re-categorize a claim using ERNIE"""
    claim = next((c for c in claims_db if c.id == claim_id), None)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    items = [item.get("description", "") for item in claim.items] if claim.items else []
    new_type = ernie_service.categorize_claim(
        claim.claimant_name,
        claim.description or "",
        claim.total_amount
    )
    
    claim.claim_type = ClaimType(new_type)
    claim.updated_at = datetime.now()
    
    return {
        "claim_id": claim_id,
        "new_type": new_type,
        "claim": claim.dict()
    }


@app.post("/api/claims/{claim_id}/validate")
async def validate_claim(claim_id: str):
    """Validate a claim and return validation results"""
    claim = next((c for c in claims_db if c.id == claim_id), None)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    # Run validation
    validation_errors = claim_processor.validate_claim(claim)
    anomalies = claim_processor.detect_anomalies(claim)
    
    # AI validation
    claim_data = claim.dict()
    ai_validation = ernie_service.validate_claim_with_ai(claim_data)
    
    return {
        "claim_id": claim_id,
        "validation_errors": validation_errors,
        "anomalies": anomalies,
        "ai_validation": ai_validation,
        "is_valid": len(validation_errors) == 0 and ai_validation.get("is_valid", True)
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
