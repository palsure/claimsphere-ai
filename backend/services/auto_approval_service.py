"""Auto-approval service with safety checks"""
from typing import List, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

from backend.database.models import (
    Claim, Plan, Decision,
    ClaimStatus, DecisionType
)
from backend.services.validation_service import ValidationService
from backend.services.audit_service import AuditService


class AutoApprovalService:
    """Service for automated claim approval with safety checks"""
    
    @staticmethod
    def evaluate_claim(
        db: Session,
        claim: Claim
    ) -> Tuple[bool, List[str]]:
        """
        Evaluate if a claim is eligible for auto-approval.
        
        Returns:
            Tuple of (is_eligible, list of reasons for decision)
        """
        reasons = []
        failed_checks = []
        
        # 1. Check if plan allows auto-approval
        if not claim.plan_id:
            failed_checks.append("No plan associated with claim")
        else:
            plan = db.query(Plan).filter(Plan.id == claim.plan_id).first()
            if not plan:
                failed_checks.append("Plan not found")
            elif not plan.auto_approve_enabled:
                failed_checks.append("Auto-approval not enabled for this plan")
            elif not plan.is_active:
                failed_checks.append("Plan is not active")
            else:
                # Check plan thresholds
                checks = AutoApprovalService._check_plan_thresholds(claim, plan)
                failed_checks.extend(checks)
                
                if not checks:
                    reasons.append(f"Plan {plan.name} allows auto-approval")
        
        # 2. Run validation rules
        validation_results = ValidationService.validate_claim(db, claim)
        validation_summary = ValidationService.get_validation_summary(validation_results)
        
        if not validation_summary["is_valid"]:
            failed_checks.extend(validation_summary["error_messages"])
        else:
            reasons.append("All validation rules passed")
        
        # 3. Check for warnings that might need review
        if validation_summary["warnings"]:
            failed_checks.append(f"Validation warnings present: {len(validation_summary['warnings'])}")
        
        # 4. Check extraction confidence
        if claim.extraction_confidence is not None:
            plan = db.query(Plan).filter(Plan.id == claim.plan_id).first() if claim.plan_id else None
            min_confidence = plan.min_confidence_score if plan else 0.85
            
            if claim.extraction_confidence < min_confidence:
                failed_checks.append(
                    f"Extraction confidence {claim.extraction_confidence:.0%} below threshold {min_confidence:.0%}"
                )
            else:
                reasons.append(f"Extraction confidence {claim.extraction_confidence:.0%} meets threshold")
        
        # 5. Check fraud risk score
        if claim.fraud_risk_score > 0:
            plan = db.query(Plan).filter(Plan.id == claim.plan_id).first() if claim.plan_id else None
            max_fraud = plan.max_fraud_risk_score if plan else 0.2
            
            if claim.fraud_risk_score > max_fraud:
                failed_checks.append(
                    f"Fraud risk score {claim.fraud_risk_score:.0%} exceeds threshold {max_fraud:.0%}"
                )
            else:
                reasons.append(f"Fraud risk score {claim.fraud_risk_score:.0%} within acceptable range")
        
        # Determine eligibility
        is_eligible = len(failed_checks) == 0
        
        if is_eligible:
            claim.auto_approval_eligible = True
            claim.auto_approval_reasons = reasons
        else:
            claim.auto_approval_eligible = False
            claim.auto_approval_reasons = failed_checks
        
        db.commit()
        
        return (is_eligible, failed_checks if failed_checks else reasons)
    
    @staticmethod
    def _check_plan_thresholds(claim: Claim, plan: Plan) -> List[str]:
        """Check claim against plan's auto-approval thresholds"""
        failed = []
        
        # Amount cap
        if plan.auto_approve_amount_cap > 0:
            if claim.total_amount > plan.auto_approve_amount_cap:
                failed.append(
                    f"Amount ${claim.total_amount} exceeds auto-approve cap ${plan.auto_approve_amount_cap}"
                )
        
        # OCR quality
        if claim.ocr_quality_score is not None:
            if claim.ocr_quality_score < plan.min_ocr_quality_score:
                failed.append(
                    f"OCR quality {claim.ocr_quality_score:.0%} below threshold {plan.min_ocr_quality_score:.0%}"
                )
        
        # Duplicate score
        if claim.duplicate_score > plan.max_duplicate_score:
            failed.append(
                f"Duplicate score {claim.duplicate_score:.0%} exceeds threshold {plan.max_duplicate_score:.0%}"
            )
        
        # Required documents
        if plan.required_documents:
            uploaded_types = [doc.document_type for doc in claim.documents if doc.document_type]
            missing = [t for t in plan.required_documents if t not in uploaded_types]
            if missing:
                failed.append(f"Missing required documents: {', '.join(missing)}")
        
        return failed
    
    @staticmethod
    def auto_approve_claim(
        db: Session,
        claim: Claim
    ) -> Decision:
        """
        Automatically approve a claim.
        
        This should only be called after evaluate_claim returns True.
        """
        if not claim.auto_approval_eligible:
            raise ValueError("Claim is not eligible for auto-approval")
        
        # Create auto-decision
        decision = Decision(
            claim_id=claim.id,
            decided_by_user_id=None,  # System decision
            decision=DecisionType.APPROVED,
            reason_code="AUTO_APPROVED",
            reason_description="Claim met all auto-approval criteria",
            notes=f"Auto-approved based on: {', '.join(claim.auto_approval_reasons or [])}",
            approved_amount=claim.total_amount,
            is_auto_decision=True,
            auto_decision_reasons=claim.auto_approval_reasons
        )
        db.add(decision)
        
        # Update claim status
        claim.status = ClaimStatus.AUTO_APPROVED
        claim.approved_amount = claim.total_amount
        claim.processed_at = datetime.utcnow()
        claim.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(decision)
        
        # Audit log
        AuditService.log(
            db=db,
            entity_type="claim",
            entity_id=claim.id,
            action="auto_approve",
            after_json={
                "status": claim.status.value,
                "approved_amount": claim.approved_amount,
                "reasons": claim.auto_approval_reasons
            }
        )
        
        return decision
    
    @staticmethod
    def route_to_agent_queue(
        db: Session,
        claim: Claim,
        reasons: List[str]
    ):
        """
        Route a claim to the agent review queue.
        
        This is called when a claim fails auto-approval checks.
        """
        claim.status = ClaimStatus.PENDING_REVIEW
        claim.auto_approval_eligible = False
        claim.auto_approval_reasons = reasons
        claim.updated_at = datetime.utcnow()
        
        db.commit()
        
        # Audit log
        AuditService.log(
            db=db,
            entity_type="claim",
            entity_id=claim.id,
            action="route_to_review",
            after_json={
                "status": claim.status.value,
                "reasons": reasons
            }
        )
    
    @staticmethod
    def process_claim(
        db: Session,
        claim: Claim
    ) -> Dict[str, Any]:
        """
        Process a claim through the auto-approval pipeline.
        
        This is the main entry point for claim processing.
        """
        result = {
            "claim_id": claim.id,
            "claim_number": claim.claim_number,
            "action": None,
            "reasons": []
        }
        
        # Evaluate eligibility
        is_eligible, reasons = AutoApprovalService.evaluate_claim(db, claim)
        result["reasons"] = reasons
        
        if is_eligible:
            # Auto-approve
            decision = AutoApprovalService.auto_approve_claim(db, claim)
            result["action"] = "auto_approved"
            result["decision_id"] = decision.id
            result["approved_amount"] = claim.approved_amount
        else:
            # Route to agent queue
            AutoApprovalService.route_to_agent_queue(db, claim, reasons)
            result["action"] = "routed_to_review"
        
        return result

