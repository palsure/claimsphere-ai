"""Claim processing service"""
from __future__ import annotations

import uuid
import hashlib
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from backend.database.models import (
    Claim, ClaimDocument, ExtractedField, 
    ClaimStatus, ClaimCategory, FieldSource
)
from backend.services.audit_service import AuditService


class ClaimService:
    """Service for claim operations"""
    
    @staticmethod
    def generate_claim_number() -> str:
        """Generate a unique claim number"""
        date_part = datetime.now().strftime("%Y%m%d")
        random_part = str(uuid.uuid4())[:8].upper()
        return f"CLM-{date_part}-{random_part}"
    
    @staticmethod
    def create_claim(
        db: Session,
        user_id: str,
        claim_data: Any  # Accept dict-like or schema object
    ) -> Claim:
        """Create a new claim"""
        # Handle both dict and pydantic model
        if hasattr(claim_data, 'model_dump'):
            data = claim_data.model_dump()
        elif hasattr(claim_data, 'dict'):
            data = claim_data.dict()
        else:
            data = claim_data if isinstance(claim_data, dict) else {}
            
        claim = Claim(
            claim_number=ClaimService.generate_claim_number(),
            user_id=user_id,
            plan_id=data.get('plan_id'),
            status=ClaimStatus.DRAFT,
            category=data.get('category', ClaimCategory.OTHER),
            total_amount=data.get('total_amount', 0),
            currency=data.get('currency', 'USD'),
            service_date=data.get('service_date'),
            provider_name=data.get('provider_name'),
            provider_npi=data.get('provider_npi'),
            diagnosis_codes=data.get('diagnosis_codes', []),
            procedure_codes=data.get('procedure_codes', []),
            description=data.get('description')
        )
        
        db.add(claim)
        db.commit()
        db.refresh(claim)
        
        return claim
    
    @staticmethod
    def transition_status(
        db: Session,
        claim: Claim,
        new_status: ClaimStatus,
        actor_user_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Claim:
        """
        Transition claim to a new status with validation.
        Logs the transition to audit log.
        """
        old_status = claim.status
        
        # Validate transition
        valid_transitions = ClaimService._get_valid_transitions(old_status)
        if new_status not in valid_transitions:
            raise ValueError(f"Invalid status transition from {old_status.value} to {new_status.value}")
        
        # Update status
        claim.status = new_status
        claim.updated_at = datetime.utcnow()
        
        # Set timestamps based on new status
        if new_status == ClaimStatus.SUBMITTED:
            claim.submitted_at = datetime.utcnow()
        elif new_status in [ClaimStatus.APPROVED, ClaimStatus.DENIED, ClaimStatus.AUTO_APPROVED]:
            claim.processed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(claim)
        
        # Log the transition
        AuditService.log_status_change(
            db=db,
            claim_id=claim.id,
            old_status=old_status.value,
            new_status=new_status.value,
            actor_user_id=actor_user_id,
            notes=notes
        )
        
        return claim
    
    @staticmethod
    def _get_valid_transitions(current_status: ClaimStatus) -> List[ClaimStatus]:
        """Get valid next statuses for a given current status"""
        transitions = {
            ClaimStatus.DRAFT: [ClaimStatus.SUBMITTED],
            ClaimStatus.SUBMITTED: [ClaimStatus.EXTRACTED, ClaimStatus.PENDING_REVIEW],
            ClaimStatus.EXTRACTED: [ClaimStatus.VALIDATED, ClaimStatus.PENDING_REVIEW],
            ClaimStatus.VALIDATED: [
                ClaimStatus.AUTO_APPROVED, 
                ClaimStatus.PENDING_REVIEW,
                ClaimStatus.APPROVED,
                ClaimStatus.DENIED
            ],
            ClaimStatus.PENDING_REVIEW: [
                ClaimStatus.APPROVED, 
                ClaimStatus.DENIED, 
                ClaimStatus.PENDED
            ],
            ClaimStatus.PENDED: [
                ClaimStatus.SUBMITTED,  # Resubmit after providing info
                ClaimStatus.APPROVED,
                ClaimStatus.DENIED
            ],
            ClaimStatus.AUTO_APPROVED: [ClaimStatus.CLOSED],
            ClaimStatus.APPROVED: [ClaimStatus.CLOSED],
            ClaimStatus.DENIED: [ClaimStatus.CLOSED],
            ClaimStatus.CLOSED: []  # Terminal state
        }
        return transitions.get(current_status, [])
    
    @staticmethod
    async def create_claim_from_document(
        db: Session,
        user_id: str,
        file: Any,  # UploadFile from FastAPI
        process_with_ai: bool = True
    ) -> Claim:
        """Create a new claim from an uploaded document"""
        import hashlib
        from backend.database.models import DuplicateMatch
        
        # Read file content
        file_bytes = await file.read()
        file_hash = hashlib.sha256(file_bytes).hexdigest()
        
        # Check for exact file duplicate (same file uploaded before)
        existing_doc = db.query(ClaimDocument).filter(
            ClaimDocument.file_hash == file_hash
        ).first()
        
        is_file_duplicate = existing_doc is not None
        original_claim_id = existing_doc.claim_id if existing_doc else None
        
        # Create the claim first
        claim = Claim(
            claim_number=ClaimService.generate_claim_number(),
            user_id=user_id,
            status=ClaimStatus.SUBMITTED,
            category=ClaimCategory.OTHER,
            total_amount=0,
            currency='USD',
            duplicate_score=1.0 if is_file_duplicate else 0.0  # Mark as duplicate if same file
        )
        
        db.add(claim)
        db.flush()  # Get the ID
        
        # If exact file duplicate, create duplicate match record
        if is_file_duplicate and original_claim_id:
            existing_match = db.query(DuplicateMatch).filter(
                DuplicateMatch.claim_id == claim.id,
                DuplicateMatch.matched_claim_id == original_claim_id
            ).first()
            
            if not existing_match:
                match = DuplicateMatch(
                    claim_id=claim.id,
                    matched_claim_id=original_claim_id,
                    similarity_score=1.0,  # Exact match
                    match_reasons_json={"reasons": ["Exact file duplicate (same file hash)"]}
                )
                db.add(match)
            claim.duplicate_score = 1.0
        
        # Create document record
        file_url = f"/uploads/{claim.id}/{file.filename}"
        
        document = ClaimDocument(
            claim_id=claim.id,
            file_name=file.filename,
            file_url=file_url,
            file_hash=file_hash,
            file_type=file.content_type,
            file_size=len(file_bytes)
        )
        
        db.add(document)
        
        # Process OCR and extract fields if enabled
        if process_with_ai and file.content_type and (
            file.content_type.startswith("image/") or 
            file.content_type == "application/pdf"
        ):
            try:
                # Process OCR
                ocr_result = await ClaimService._process_ocr(file_bytes, file.content_type)
                document.ocr_text = ocr_result.get("text", "")
                document.ocr_quality_score = ocr_result.get("quality_score", 0.0)
                document.ocr_result_json = ocr_result
                
                # Update claim OCR quality
                claim.ocr_quality_score = ocr_result.get("quality_score", 0.0)
                
                # Extract fields using ERNIE (also sets category)
                await ClaimService._extract_fields(db, claim, ocr_result, user_id)
                
                # Update status to EXTRACTED after processing
                claim.status = ClaimStatus.EXTRACTED
                
                # Check for content-based duplicates (similar claims)
                if not is_file_duplicate:
                    duplicates = ClaimService.find_duplicates(db, claim, threshold=0.6)
                    if duplicates:
                        # duplicate_score is already set by find_duplicates
                        print(f"Found {len(duplicates)} potential duplicate(s) for claim {claim.claim_number}")
                
            except Exception as e:
                print(f"OCR/AI processing error: {e}")
                # Still save the claim even if processing fails
        
        db.commit()
        db.refresh(claim)
        
        return claim
    
    @staticmethod
    async def add_document(
        db: Session,
        claim: Claim,
        file: Any,  # UploadFile from FastAPI
        user_id: str
    ) -> Claim:
        """Add a document to a claim and process it"""
        # Read file content
        file_bytes = await file.read()
        file_hash = hashlib.sha256(file_bytes).hexdigest()
        
        # Check for duplicate document
        existing = db.query(ClaimDocument).filter(
            ClaimDocument.claim_id == claim.id,
            ClaimDocument.file_hash == file_hash
        ).first()
        
        if existing:
            return claim  # Skip duplicate
        
        # Create document record
        # In production, upload to cloud storage and get URL
        file_url = f"/uploads/{claim.id}/{file.filename}"
        
        document = ClaimDocument(
            claim_id=claim.id,
            file_name=file.filename,
            file_url=file_url,
            file_hash=file_hash,
            file_type=file.content_type,
            file_size=len(file_bytes)
        )
        
        db.add(document)
        
        # Process OCR if it's an image or PDF
        if file.content_type and (
            file.content_type.startswith("image/") or 
            file.content_type == "application/pdf"
        ):
            try:
                ocr_result = await ClaimService._process_ocr(file_bytes, file.content_type)
                document.ocr_text = ocr_result.get("text", "")
                document.ocr_quality_score = ocr_result.get("quality_score", 0.0)
                document.ocr_result_json = ocr_result
                
                # Extract fields from OCR
                await ClaimService._extract_fields(db, claim, ocr_result, user_id)
                
                # Update claim OCR quality score (average of all documents)
                all_docs = db.query(ClaimDocument).filter(
                    ClaimDocument.claim_id == claim.id
                ).all()
                scores = [d.ocr_quality_score for d in all_docs if d.ocr_quality_score]
                if scores:
                    claim.ocr_quality_score = sum(scores) / len(scores)
            except Exception as e:
                print(f"OCR processing error: {e}")
        
        db.commit()
        db.refresh(claim)
        
        return claim
    
    # Class-level singleton for OCRProcessor to avoid reinitializing on every request
    _ocr_processor = None
    
    @classmethod
    def _get_ocr_processor(cls):
        """Get or create singleton OCRProcessor"""
        if cls._ocr_processor is None:
            print("[ClaimService] Initializing OCRProcessor singleton...")
            from backend.ocr_processor import OCRProcessor
            cls._ocr_processor = OCRProcessor(lang='en')
            print("[ClaimService] OCRProcessor singleton ready")
        return cls._ocr_processor
    
    @staticmethod
    async def _process_ocr(file_bytes: bytes, content_type: str) -> Dict[str, Any]:
        """Process OCR on document"""
        try:
            import time
            start_time = time.time()
            
            ocr = ClaimService._get_ocr_processor()
            if ocr.ocr is None:
                print("OCR Error: PaddleOCR not initialized")
                return {"text": "", "quality_score": 0.0, "error": "OCR not available"}
            
            file_type = "pdf" if "pdf" in content_type else "image"
            result = ocr.process_bytes(file_bytes, file_type)
            
            elapsed = time.time() - start_time
            
            # Debug: Print OCR result summary
            extracted_text = result.get("text", "")
            print(f"OCR completed in {elapsed:.2f}s - extracted {len(extracted_text)} chars, quality: {result.get('quality_score', 0)}")
            if extracted_text:
                # Print first 500 chars for debugging
                print(f"OCR text preview: {extracted_text[:500]}...")
            
            return result
        except Exception as e:
            print(f"OCR Error: {e}")
            import traceback
            traceback.print_exc()
            return {"text": "", "quality_score": 0.0, "error": str(e)}
    
    @staticmethod
    async def _extract_fields(
        db: Session,
        claim: Claim,
        ocr_result: Dict[str, Any],
        user_id: str
    ):
        """Extract fields from OCR result using ERNIE"""
        try:
            from backend.ernie_service import ErnieService
            
            ernie = ErnieService()
            ocr_text = ocr_result.get("text", "")
            
            print(f"Extracting fields from {len(ocr_text)} chars of OCR text")
            
            extracted_data = ernie.extract_claim_info(
                ocr_text,
                ocr_result.get("layout", [])
            )
            
            print(f"Extracted data: claimant_name={extracted_data.get('claimant_name')}, "
                  f"amount={extracted_data.get('total_amount')}, "
                  f"provider={extracted_data.get('provider_name')}, "
                  f"type={extracted_data.get('claim_type')}")
            
            # Calculate overall confidence
            confidences = []
            
            # Store extracted fields
            field_mappings = [
                ("claimant_name", extracted_data.get("claimant_name")),
                ("date_of_incident", extracted_data.get("date_of_incident")),
                ("total_amount", str(extracted_data.get("total_amount", ""))),
                ("currency", extracted_data.get("currency")),
                ("provider_name", extracted_data.get("provider_name")),
                ("policy_number", extracted_data.get("policy_number")),
                ("diagnosis", extracted_data.get("diagnosis")),
                ("procedure", extracted_data.get("procedure")),
                ("claim_type", extracted_data.get("claim_type")),
                ("description", extracted_data.get("description")),
            ]
            
            for field_name, value in field_mappings:
                if value:
                    # Check if field already exists
                    existing = db.query(ExtractedField).filter(
                        ExtractedField.claim_id == claim.id,
                        ExtractedField.field_name == field_name
                    ).first()
                    
                    confidence = 0.85  # Default confidence
                    confidences.append(confidence)
                    
                    if existing:
                        # Update existing field if from OCR
                        if existing.source == FieldSource.OCR:
                            existing.value = str(value)
                            existing.confidence = confidence
                    else:
                        field = ExtractedField(
                            claim_id=claim.id,
                            field_name=field_name,
                            value=str(value),
                            confidence=confidence,
                            source=FieldSource.OCR
                        )
                        db.add(field)
            
            # Update claim extraction confidence
            if confidences:
                claim.extraction_confidence = sum(confidences) / len(confidences)
            
            # Update claim fields if not already set
            if extracted_data.get("total_amount") and not claim.total_amount:
                try:
                    claim.total_amount = float(extracted_data.get("total_amount", 0))
                except (ValueError, TypeError):
                    pass
                    
            if extracted_data.get("provider_name") and not claim.provider_name:
                claim.provider_name = extracted_data.get("provider_name")
                
            if extracted_data.get("date_of_incident") and not claim.service_date:
                try:
                    from datetime import datetime
                    date_str = extracted_data["date_of_incident"]
                    claim.service_date = datetime.fromisoformat(date_str)
                except:
                    pass
            
            # Auto-categorize based on extracted claim_type
            if extracted_data.get("claim_type"):
                detected_type = extracted_data["claim_type"].lower().strip()
                category_map = {
                    "medical": ClaimCategory.MEDICAL,
                    "dental": ClaimCategory.DENTAL,
                    "vision": ClaimCategory.VISION,
                    "pharmacy": ClaimCategory.PHARMACY,
                    "mental_health": ClaimCategory.MENTAL_HEALTH,
                    "hospital": ClaimCategory.HOSPITAL,
                    "emergency": ClaimCategory.EMERGENCY,
                    "preventive": ClaimCategory.PREVENTIVE,
                    "insurance": ClaimCategory.OTHER,  # Map generic insurance to other
                    "travel": ClaimCategory.OTHER,
                    "property": ClaimCategory.OTHER,
                    "business": ClaimCategory.OTHER,
                    "health": ClaimCategory.MEDICAL,
                    "prescription": ClaimCategory.PHARMACY,
                    "doctor": ClaimCategory.MEDICAL,
                }
                claim.category = category_map.get(detected_type, ClaimCategory.OTHER)
                print(f"Auto-categorized claim as: {claim.category.value} (detected: {detected_type})")
            
            # Also try keyword-based categorization from OCR text if no type detected
            if claim.category == ClaimCategory.OTHER and ocr_result.get("text"):
                text_lower = ocr_result.get("text", "").lower()
                if any(kw in text_lower for kw in ['dental', 'dentist', 'tooth', 'teeth', 'orthodont']):
                    claim.category = ClaimCategory.DENTAL
                elif any(kw in text_lower for kw in ['vision', 'eye', 'optical', 'glasses', 'lens', 'optometr']):
                    claim.category = ClaimCategory.VISION
                elif any(kw in text_lower for kw in ['pharmacy', 'prescription', 'rx', 'drug', 'medication']):
                    claim.category = ClaimCategory.PHARMACY
                elif any(kw in text_lower for kw in ['mental', 'psych', 'counsel', 'therapy', 'behavioral']):
                    claim.category = ClaimCategory.MENTAL_HEALTH
                elif any(kw in text_lower for kw in ['hospital', 'inpatient', 'admission']):
                    claim.category = ClaimCategory.HOSPITAL
                elif any(kw in text_lower for kw in ['emergency', 'er ', 'urgent care', 'ambulance']):
                    claim.category = ClaimCategory.EMERGENCY
                elif any(kw in text_lower for kw in ['preventive', 'annual', 'checkup', 'physical', 'vaccine', 'screening']):
                    claim.category = ClaimCategory.PREVENTIVE
                elif any(kw in text_lower for kw in ['medical', 'doctor', 'clinic', 'physician', 'health', 'patient']):
                    claim.category = ClaimCategory.MEDICAL
                    
                if claim.category != ClaimCategory.OTHER:
                    print(f"Keyword-based category: {claim.category.value}")
                    
        except Exception as e:
            print(f"Field extraction error: {e}")
    
    @staticmethod
    def find_duplicates(
        db: Session,
        claim: Claim,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Find potential duplicate claims"""
        from backend.database.models import DuplicateMatch
        
        duplicates = []
        
        # Query similar claims (same user, similar amount, recent dates)
        similar_claims = db.query(Claim).filter(
            Claim.id != claim.id,
            Claim.user_id == claim.user_id,
            Claim.status.notin_([ClaimStatus.DRAFT, ClaimStatus.DENIED])
        ).all()
        
        for other in similar_claims:
            similarity_score = 0.0
            match_reasons = []
            
            # Check amount similarity (within 5%)
            if claim.total_amount and other.total_amount:
                amount_diff = abs(claim.total_amount - other.total_amount) / max(claim.total_amount, 1)
                if amount_diff < 0.05:
                    similarity_score += 0.3
                    match_reasons.append(f"Similar amount: ${claim.total_amount} vs ${other.total_amount}")
            
            # Check service date (within 7 days)
            if claim.service_date and other.service_date:
                date_diff = abs((claim.service_date - other.service_date).days)
                if date_diff <= 7:
                    similarity_score += 0.3
                    match_reasons.append(f"Similar date: {date_diff} days apart")
            
            # Check provider
            if claim.provider_name and other.provider_name:
                if claim.provider_name.lower() == other.provider_name.lower():
                    similarity_score += 0.2
                    match_reasons.append(f"Same provider: {claim.provider_name}")
            
            # Check category
            if claim.category == other.category:
                similarity_score += 0.1
                match_reasons.append(f"Same category: {claim.category.value}")
            
            # Check procedure codes
            if claim.procedure_codes and other.procedure_codes:
                common_codes = set(claim.procedure_codes) & set(other.procedure_codes)
                if common_codes:
                    similarity_score += 0.1
                    match_reasons.append(f"Common procedure codes: {common_codes}")
            
            if similarity_score >= threshold:
                duplicates.append({
                    "matched_claim": other,
                    "similarity_score": min(similarity_score, 1.0),
                    "match_reasons": match_reasons
                })
                
                # Create duplicate match record
                existing_match = db.query(DuplicateMatch).filter(
                    DuplicateMatch.claim_id == claim.id,
                    DuplicateMatch.matched_claim_id == other.id
                ).first()
                
                if not existing_match:
                    match = DuplicateMatch(
                        claim_id=claim.id,
                        matched_claim_id=other.id,
                        similarity_score=min(similarity_score, 1.0),
                        match_reasons_json={"reasons": match_reasons}
                    )
                    db.add(match)
        
        if duplicates:
            claim.duplicate_score = max(d["similarity_score"] for d in duplicates)
            db.commit()
        
        return duplicates

