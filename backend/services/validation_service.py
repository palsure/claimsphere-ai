"""Validation engine service"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import logging
import os

from backend.database.models import (
    Claim, ValidationRule, ValidationResult,
    MemberPolicy, ClaimStatus, PolicyStatus
)

logger = logging.getLogger(__name__)


class ValidationService:
    """Service for claim validation"""
    
    @staticmethod
    def validate_claim(
        db: Session,
        claim: Claim,
        use_ai_validation: Optional[bool] = None,
        force_rerun: bool = False
    ) -> List[ValidationResult]:
        """
        Run all applicable validation rules on a claim.
        Optionally includes AI-powered validation from CAMEL-AI.
        Returns list of ValidationResult objects.
        
        Args:
            force_rerun: If True, run validation even if results already exist
        """
        # Check if validation results already exist (unless force_rerun)
        if not force_rerun:
            existing_results = db.query(ValidationResult).filter(
                ValidationResult.claim_id == claim.id
            ).all()
            if existing_results:
                logger.info(f"Validation results already exist for claim {claim.id}, returning existing results")
                return existing_results
        
        # Read from environment if not explicitly provided
        if use_ai_validation is None:
            use_ai_validation = os.getenv("USE_AI_VALIDATION", "true").lower() in ("true", "1", "yes")
        
        results = []
        
        # Get applicable rules (global + plan-specific)
        rules = db.query(ValidationRule).filter(
            ValidationRule.is_active == True,
            (ValidationRule.plan_id == None) | (ValidationRule.plan_id == claim.plan_id)
        ).order_by(ValidationRule.order).all()
        
        # Run rule-based validation
        for rule in rules:
            result = ValidationService._evaluate_rule(db, claim, rule)
            results.append(result)
            db.add(result)
        
        # Always check for duplicates as a built-in validation rule
        duplicate_result = ValidationService._check_duplicate_claim(db, claim)
        if duplicate_result:
            results.append(duplicate_result)
            db.add(duplicate_result)
        
        # If no rules exist and no duplicate check failed, create a basic validation result
        if len(results) == 0:
            basic_result = ValidationResult(
                claim_id=claim.id,
                rule_id=None,
                rule_name="Basic Validation",
                passed=True,
                severity="info",
                message="No validation rules configured. Basic validation passed.",
                details_json={"source": "system", "has_rules": False}
            )
            results.append(basic_result)
            db.add(basic_result)
        
        # Run AI-powered validation if enabled
        if use_ai_validation:
            try:
                ai_results = ValidationService._run_ai_validation(db, claim)
                results.extend(ai_results)
                for result in ai_results:
                    db.add(result)
            except Exception as e:
                logger.error(f"AI validation failed: {e}", exc_info=True)
                # Continue without AI validation if it fails
        
        db.commit()
        
        return results
    
    @staticmethod
    def _run_ai_validation(db: Session, claim: Claim) -> List[ValidationResult]:
        """Run AI-powered validation using CAMEL-AI ValidationAgent"""
        results = []
        
        try:
            from backend.services.agent_coordinator import get_agent_coordinator
            
            coordinator = get_agent_coordinator()
            coordinator.initialize()  # Use correct method name
            
            # Prepare claim data for validation agent
            claim_data = {
                "id": claim.id,
                "claim_number": claim.claim_number,
                "claimant_name": ValidationService._get_claimant_name(claim),
                "date_of_incident": claim.service_date.isoformat() if claim.service_date else None,
                "total_amount": float(claim.total_amount),
                "currency": claim.currency,
                "claim_type": claim.category.value if hasattr(claim.category, 'value') else str(claim.category),
                "provider_name": claim.provider_name,
                "policy_number": None,  # Would need to get from plan/member
                "description": claim.description,
            }
            
            # Get extracted fields if available
            if claim.extracted_fields:
                for field in claim.extracted_fields:
                    if field.field_name not in claim_data:
                        claim_data[field.field_name] = field.value
            
            # Run validation agent
            validation_result = coordinator.validate_claim(
                {"extracted_data": claim_data}
            )
            
            if validation_result.get("success"):
                # Convert errors to ValidationResult objects
                errors = validation_result.get("errors", [])
                warnings = validation_result.get("warnings", [])
                
                for error_msg in errors:
                    result = ValidationResult(
                        claim_id=claim.id,
                        rule_id=None,  # AI validation doesn't have a specific rule
                        rule_name="AI Validation - Error",
                        passed=False,
                        severity="error",
                        message=error_msg,
                        details_json={
                            "source": "camel_ai_validation_agent",
                            "reasoning": validation_result.get("reasoning", "")
                        }
                    )
                    results.append(result)
                
                for warning_msg in warnings:
                    result = ValidationResult(
                        claim_id=claim.id,
                        rule_id=None,
                        rule_name="AI Validation - Warning",
                        passed=True,  # Warnings don't fail validation
                        severity="warning",
                        message=warning_msg,
                        details_json={
                            "source": "camel_ai_validation_agent",
                            "reasoning": validation_result.get("reasoning", "")
                        }
                    )
                    results.append(result)
                
                # If validation passed with no errors/warnings, add a success result
                if len(errors) == 0 and len(warnings) == 0:
                    result = ValidationResult(
                        claim_id=claim.id,
                        rule_id=None,
                        rule_name="AI Validation - Overall",
                        passed=True,
                        severity="info",
                        message="AI validation completed successfully with no issues found",
                        details_json={
                            "source": "camel_ai_validation_agent",
                            "reasoning": validation_result.get("reasoning", ""),
                            "is_valid": validation_result.get("is_valid", True)
                        }
                    )
                    results.append(result)
                    
        except ImportError:
            logger.warning("CAMEL-AI not available for validation")
        except Exception as e:
            logger.error(f"Error running AI validation: {e}", exc_info=True)
        
        return results
    
    @staticmethod
    def _get_claimant_name(claim: Claim) -> Optional[str]:
        """Get claimant name from extracted fields or claim"""
        if claim.extracted_fields:
            for field in claim.extracted_fields:
                if field.field_name == 'claimant_name' and field.value:
                    return field.value
        return None
    
    @staticmethod
    def _evaluate_rule(
        db: Session,
        claim: Claim,
        rule: ValidationRule
    ) -> ValidationResult:
        """Evaluate a single validation rule"""
        condition = rule.condition_json
        rule_type = rule.rule_type
        
        passed = True
        message = None
        details = {}
        
        try:
            if rule_type == "amount_limit":
                passed, message, details = ValidationService._check_amount_limit(claim, condition)
            
            elif rule_type == "date_range":
                passed, message, details = ValidationService._check_date_range(claim, condition)
            
            elif rule_type == "required_fields":
                passed, message, details = ValidationService._check_required_fields(claim, condition)
            
            elif rule_type == "required_documents":
                passed, message, details = ValidationService._check_required_documents(claim, condition)
            
            elif rule_type == "eligibility":
                passed, message, details = ValidationService._check_eligibility(db, claim, condition)
            
            elif rule_type == "duplicate_check":
                passed, message, details = ValidationService._check_duplicates(claim, condition)
            
            elif rule_type == "provider_validation":
                passed, message, details = ValidationService._check_provider(claim, condition)
            
            elif rule_type == "category_rules":
                passed, message, details = ValidationService._check_category_rules(claim, condition)
            
            else:
                message = f"Unknown rule type: {rule_type}"
                details = {"rule_type": rule_type}
                
        except Exception as e:
            passed = False
            message = f"Rule evaluation error: {str(e)}"
            details = {"error": str(e)}
        
        return ValidationResult(
            claim_id=claim.id,
            rule_id=rule.id,
            rule_name=rule.name,
            passed=passed,
            severity=rule.severity,
            message=message or rule.error_message,
            details_json=details
        )
    
    @staticmethod
    def _check_amount_limit(
        claim: Claim,
        condition: Dict[str, Any]
    ) -> tuple:
        """Check if claim amount is within limits"""
        max_amount = condition.get("max_amount")
        min_amount = condition.get("min_amount", 0)
        
        if claim.total_amount < min_amount:
            return (
                False,
                f"Claim amount ${claim.total_amount} is below minimum ${min_amount}",
                {"amount": claim.total_amount, "min": min_amount}
            )
        
        if max_amount and claim.total_amount > max_amount:
            return (
                False,
                f"Claim amount ${claim.total_amount} exceeds maximum ${max_amount}",
                {"amount": claim.total_amount, "max": max_amount}
            )
        
        return (True, None, {"amount": claim.total_amount})
    
    @staticmethod
    def _check_date_range(
        claim: Claim,
        condition: Dict[str, Any]
    ) -> tuple:
        """Check if service date is within valid range"""
        max_days_past = condition.get("max_days_past", 365)
        max_days_future = condition.get("max_days_future", 0)
        
        if not claim.service_date:
            return (False, "Service date is required", {})
        
        today = datetime.utcnow().date()
        service_date = claim.service_date.date() if isinstance(claim.service_date, datetime) else claim.service_date
        
        days_diff = (today - service_date).days
        
        if days_diff > max_days_past:
            return (
                False,
                f"Service date is {days_diff} days ago, maximum is {max_days_past} days",
                {"days_past": days_diff, "max_allowed": max_days_past}
            )
        
        if days_diff < -max_days_future:
            return (
                False,
                f"Service date is {-days_diff} days in the future, maximum is {max_days_future} days",
                {"days_future": -days_diff, "max_allowed": max_days_future}
            )
        
        return (True, None, {"service_date": str(service_date)})
    
    @staticmethod
    def _check_required_fields(
        claim: Claim,
        condition: Dict[str, Any]
    ) -> tuple:
        """Check if required fields are present"""
        required_fields = condition.get("fields", [])
        missing = []
        
        for field in required_fields:
            value = getattr(claim, field, None)
            if value is None or value == "" or value == []:
                missing.append(field)
        
        if missing:
            return (
                False,
                f"Missing required fields: {', '.join(missing)}",
                {"missing_fields": missing}
            )
        
        return (True, None, {"checked_fields": required_fields})
    
    @staticmethod
    def _check_required_documents(
        claim: Claim,
        condition: Dict[str, Any]
    ) -> tuple:
        """Check if required document types are uploaded"""
        required_types = condition.get("document_types", [])
        
        if not required_types:
            return (True, None, {})
        
        uploaded_types = [doc.document_type for doc in claim.documents if doc.document_type]
        missing = [t for t in required_types if t not in uploaded_types]
        
        if missing:
            return (
                False,
                f"Missing required documents: {', '.join(missing)}",
                {"missing_documents": missing, "uploaded": uploaded_types}
            )
        
        return (True, None, {"uploaded_documents": uploaded_types})
    
    @staticmethod
    def _check_eligibility(
        db: Session,
        claim: Claim,
        condition: Dict[str, Any]
    ) -> tuple:
        """Check member eligibility based on policy dates"""
        require_active = condition.get("require_active_policy", True)
        
        if not claim.plan_id:
            if require_active:
                return (False, "No plan associated with claim", {})
            return (True, None, {})
        
        # Find member's policy
        policy = db.query(MemberPolicy).filter(
            MemberPolicy.user_id == claim.user_id,
            MemberPolicy.plan_id == claim.plan_id
        ).first()
        
        if not policy:
            return (
                False,
                "No policy found for this member and plan",
                {"user_id": claim.user_id, "plan_id": claim.plan_id}
            )
        
        if policy.status != PolicyStatus.ACTIVE:
            return (
                False,
                f"Policy is not active (status: {policy.status.value})",
                {"policy_status": policy.status.value}
            )
        
        # Check if service date is within policy dates
        service_date = claim.service_date
        if service_date:
            if policy.start_date and service_date < policy.start_date:
                return (
                    False,
                    "Service date is before policy start date",
                    {"service_date": str(service_date), "policy_start": str(policy.start_date)}
                )
            
            if policy.end_date and service_date > policy.end_date:
                return (
                    False,
                    "Service date is after policy end date",
                    {"service_date": str(service_date), "policy_end": str(policy.end_date)}
                )
        
        return (True, None, {"policy_id": policy.id, "member_id": policy.member_id})
    
    @staticmethod
    def _check_duplicates(
        claim: Claim,
        condition: Dict[str, Any]
    ) -> tuple:
        """Check for potential duplicate claims"""
        threshold = condition.get("similarity_threshold", 0.85)
        
        if claim.duplicate_score >= threshold:
            return (
                False,
                f"Potential duplicate detected (similarity: {claim.duplicate_score:.0%})",
                {"duplicate_score": claim.duplicate_score, "threshold": threshold}
            )
        
        return (True, None, {"duplicate_score": claim.duplicate_score})
    
    @staticmethod
    def _check_duplicate_claim(db: Session, claim: Claim) -> Optional[ValidationResult]:
        """
        Built-in duplicate check validation rule.
        Automatically rejects claims with high duplicate scores.
        """
        from backend.database.models import DuplicateMatch
        
        # Check duplicate score
        duplicate_threshold = 0.85  # 85% similarity threshold
        
        if claim.duplicate_score >= duplicate_threshold:
            # Get duplicate matches for details
            duplicate_matches = db.query(DuplicateMatch).filter(
                DuplicateMatch.claim_id == claim.id
            ).all()
            
            matched_claim_numbers = []
            if duplicate_matches:
                for match in duplicate_matches:
                    matched_claim = db.query(Claim).filter(Claim.id == match.matched_claim_id).first()
                    if matched_claim:
                        matched_claim_numbers.append(matched_claim.claim_number)
            
            message = f"Duplicate claim detected (similarity: {claim.duplicate_score:.0%})"
            if matched_claim_numbers:
                message += f". Matches: {', '.join(matched_claim_numbers[:3])}"
                if len(matched_claim_numbers) > 3:
                    message += f" and {len(matched_claim_numbers) - 3} more"
            
            return ValidationResult(
                claim_id=claim.id,
                rule_id=None,
                rule_name="Duplicate Detection",
                passed=False,
                severity="error",
                message=message,
                details_json={
                    "source": "system",
                    "duplicate_score": claim.duplicate_score,
                    "threshold": duplicate_threshold,
                    "matched_claims": matched_claim_numbers,
                    "auto_reject": True
                }
            )
        
        return None
    
    @staticmethod
    def _check_provider(
        claim: Claim,
        condition: Dict[str, Any]
    ) -> tuple:
        """Validate provider information"""
        require_npi = condition.get("require_npi", False)
        allowed_types = condition.get("allowed_provider_types", [])
        
        if require_npi and not claim.provider_npi:
            return (
                False,
                "Provider NPI is required",
                {"require_npi": True}
            )
        
        # NPI format validation (10 digits)
        if claim.provider_npi:
            if not claim.provider_npi.isdigit() or len(claim.provider_npi) != 10:
                return (
                    False,
                    "Invalid NPI format (must be 10 digits)",
                    {"npi": claim.provider_npi}
                )
        
        return (True, None, {"provider_name": claim.provider_name, "npi": claim.provider_npi})
    
    @staticmethod
    def _check_category_rules(
        claim: Claim,
        condition: Dict[str, Any]
    ) -> tuple:
        """Category-specific validation rules"""
        target_category = condition.get("category")
        
        if claim.category.value != target_category:
            return (True, None, {"skipped": "Category mismatch"})
        
        max_amount = condition.get("max_amount")
        if max_amount and claim.total_amount > max_amount:
            return (
                False,
                f"Amount exceeds {target_category} category limit of ${max_amount}",
                {"amount": claim.total_amount, "category_limit": max_amount}
            )
        
        required_codes = condition.get("required_codes", [])
        if required_codes:
            all_codes = (claim.diagnosis_codes or []) + (claim.procedure_codes or [])
            if not any(code in all_codes for code in required_codes):
                return (
                    False,
                    f"Missing required codes for {target_category}: {required_codes}",
                    {"required": required_codes, "provided": all_codes}
                )
        
        return (True, None, {"category": target_category})
    
    @staticmethod
    def get_validation_summary(results: List[ValidationResult]) -> Dict[str, Any]:
        """Get a summary of validation results"""
        passed = [r for r in results if r.passed]
        failed = [r for r in results if not r.passed]
        
        errors = [r for r in failed if r.severity == "error"]
        warnings = [r for r in failed if r.severity == "warning"]
        
        return {
            "total_rules": len(results),
            "passed": len(passed),
            "failed": len(failed),
            "errors": len(errors),
            "warnings": len(warnings),
            "is_valid": len(errors) == 0,
            "error_messages": [r.message for r in errors],
            "warning_messages": [r.message for r in warnings]
        }

