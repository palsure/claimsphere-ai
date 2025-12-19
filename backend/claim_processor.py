"""
Business logic for claim processing, validation, and analytics
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from backend.models.claim import Claim, ClaimType, ClaimStatus, ClaimAnalytics
from backend.utils import normalize_merchant_name


class ClaimProcessor:
    """Process, validate, and analyze insurance/medical claims"""
    
    def __init__(self):
        self.claims: List[Claim] = []
    
    def add_claim(self, claim: Claim):
        """Add a claim to the processor"""
        self.claims.append(claim)
    
    def detect_duplicates(self, claim: Claim, threshold: float = 0.90) -> List[Claim]:
        """
        Detect duplicate claims
        
        Args:
            claim: Claim to check for duplicates
            threshold: Similarity threshold (0-1)
            
        Returns:
            List of duplicate claims
        """
        duplicates = []
        
        for existing_claim in self.claims:
            if existing_claim.id == claim.id:
                continue
            
            similarity = self._calculate_similarity(claim, existing_claim)
            if similarity >= threshold:
                duplicates.append(existing_claim)
        
        return duplicates
    
    def _calculate_similarity(self, claim1: Claim, claim2: Claim) -> float:
        """
        Calculate similarity between two claims
        
        Args:
            claim1: First claim
            claim2: Second claim
            
        Returns:
            Similarity score (0-1)
        """
        score = 0.0
        factors = 0
        
        # Claimant name similarity
        if claim1.claimant_name and claim2.claimant_name:
            name_sim = self._string_similarity(
                claim1.claimant_name.lower(),
                claim2.claimant_name.lower()
            )
            score += name_sim * 0.25
            factors += 0.25
        
        # Amount similarity (within 2%)
        if claim1.total_amount and claim2.total_amount:
            amount_diff = abs(claim1.total_amount - claim2.total_amount)
            amount_avg = (claim1.total_amount + claim2.total_amount) / 2
            if amount_avg > 0:
                amount_sim = max(0, 1 - (amount_diff / amount_avg))
                score += amount_sim * 0.3
                factors += 0.3
        
        # Date of incident similarity (within 7 days)
        if claim1.date_of_incident and claim2.date_of_incident:
            date_diff = abs((claim1.date_of_incident - claim2.date_of_incident).days)
            date_sim = max(0, 1 - (date_diff / 7.0))  # 7 day tolerance
            score += date_sim * 0.25
            factors += 0.25
        
        # Claim type similarity
        if claim1.claim_type == claim2.claim_type:
            score += 0.2
            factors += 0.2
        
        return score / factors if factors > 0 else 0.0
    
    def _string_similarity(self, s1: str, s2: str) -> float:
        """Simple string similarity using character overlap"""
        if s1 == s2:
            return 1.0
        
        if s1 in s2 or s2 in s1:
            return 0.8
        
        set1 = set(s1.lower())
        set2 = set(s2.lower())
        if len(set1) == 0 and len(set2) == 0:
            return 1.0
        if len(set1) == 0 or len(set2) == 0:
            return 0.0
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0
    
    def validate_claim(self, claim: Claim) -> List[str]:
        """
        Validate a claim and return list of validation errors
        
        Args:
            claim: Claim to validate
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Required fields
        if not claim.claimant_name or claim.claimant_name.strip() == "":
            errors.append("Claimant name is required")
        
        if not claim.date_of_incident:
            errors.append("Date of incident is required")
        
        if claim.total_amount <= 0:
            errors.append("Claim amount must be greater than zero")
        
        # Date validations
        if claim.date_of_incident > datetime.now():
            errors.append("Date of incident cannot be in the future")
        
        # Check if incident date is too old (more than 2 years)
        if claim.date_of_incident < datetime.now() - timedelta(days=730):
            errors.append("Date of incident is more than 2 years old")
        
        # Amount validations
        if claim.total_amount > 1000000:  # Flag unusually high claims
            errors.append("Claim amount exceeds typical maximum - requires manual review")
        
        # Policy number validation (if provided)
        if claim.policy_number and len(claim.policy_number) < 5:
            errors.append("Policy number appears to be invalid")
        
        # Supporting documents
        if not claim.supporting_documents or len(claim.supporting_documents) == 0:
            errors.append("At least one supporting document is required")
        
        return errors
    
    def detect_anomalies(self, claim: Claim) -> List[str]:
        """
        Detect anomalies in a claim
        
        Args:
            claim: Claim to check
            
        Returns:
            List of anomaly descriptions
        """
        anomalies = []
        
        # Check for unusually high amounts
        if claim.total_amount > 0:
            avg_amount = self._get_average_amount(claim.claim_type)
            if avg_amount > 0 and claim.total_amount > avg_amount * 5:
                anomalies.append(f"Unusually high amount: ${claim.total_amount:.2f} (avg for type: ${avg_amount:.2f})")
        
        # Check for future dates
        if claim.date_of_incident > datetime.now():
            anomalies.append("Date of incident is in the future")
        
        # Check for very old dates
        if claim.date_of_incident < datetime.now() - timedelta(days=730):
            anomalies.append("Date of incident is more than 2 years old")
        
        # Check for missing policy number
        if not claim.policy_number:
            anomalies.append("Policy number is missing")
        
        # Check for missing description
        if not claim.description or len(claim.description.strip()) < 10:
            anomalies.append("Claim description is too short or missing")
        
        return anomalies
    
    def _get_average_amount(self, claim_type: ClaimType) -> float:
        """Calculate average claim amount for a given type"""
        type_claims = [c for c in self.claims if c.claim_type == claim_type]
        if not type_claims:
            return 0.0
        
        total = sum(c.total_amount for c in type_claims)
        return total / len(type_claims)
    
    def generate_analytics(self, date_from: Optional[datetime] = None,
                         date_to: Optional[datetime] = None) -> ClaimAnalytics:
        """
        Generate analytics for claims
        
        Args:
            date_from: Start date filter
            date_to: End date filter
            
        Returns:
            ClaimAnalytics object
        """
        # Filter claims by date range
        filtered_claims = self.claims
        if date_from:
            filtered_claims = [c for c in filtered_claims if c.date_submitted >= date_from]
        if date_to:
            filtered_claims = [c for c in filtered_claims if c.date_submitted <= date_to]
        
        if not filtered_claims:
            return ClaimAnalytics(
                total_claims=0,
                total_amount=0.0,
                approved_amount=0.0,
                pending_amount=0.0,
                status_breakdown={},
                type_breakdown={},
                monthly_trends=[],
                average_processing_time=0.0,
                approval_rate=0.0,
                top_claimants=[]
            )
        
        # Calculate totals
        total_claims = len(filtered_claims)
        total_amount = sum(c.total_amount for c in filtered_claims)
        approved_amount = sum(c.approved_amount or 0 for c in filtered_claims if c.status == ClaimStatus.APPROVED)
        pending_amount = sum(c.total_amount for c in filtered_claims if c.status in [ClaimStatus.PENDING, ClaimStatus.UNDER_REVIEW])
        
        # Status breakdown
        status_breakdown = defaultdict(int)
        for claim in filtered_claims:
            status_breakdown[claim.status.value] += 1
        
        # Type breakdown
        type_breakdown = defaultdict(float)
        for claim in filtered_claims:
            type_breakdown[claim.claim_type.value] += claim.total_amount
        
        # Monthly trends
        monthly_trends = self._calculate_monthly_trends(filtered_claims)
        
        # Average processing time
        processed_claims = [c for c in filtered_claims if c.status in [ClaimStatus.APPROVED, ClaimStatus.REJECTED, ClaimStatus.PROCESSED]]
        if processed_claims:
            processing_times = [
                (c.updated_at - c.date_submitted).days
                for c in processed_claims
            ]
            avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0.0
        else:
            avg_processing_time = 0.0
        
        # Approval rate
        approved_count = len([c for c in filtered_claims if c.status == ClaimStatus.APPROVED])
        processed_count = len(processed_claims)
        approval_rate = (approved_count / processed_count * 100) if processed_count > 0 else 0.0
        
        # Top claimants
        top_claimants = self._get_top_claimants(filtered_claims, limit=10)
        
        return ClaimAnalytics(
            total_claims=total_claims,
            total_amount=total_amount,
            approved_amount=approved_amount,
            pending_amount=pending_amount,
            status_breakdown=dict(status_breakdown),
            type_breakdown=dict(type_breakdown),
            monthly_trends=monthly_trends,
            average_processing_time=avg_processing_time,
            approval_rate=approval_rate,
            top_claimants=top_claimants
        )
    
    def _calculate_monthly_trends(self, claims: List[Claim]) -> List[Dict]:
        """Calculate monthly claim trends"""
        monthly_data = defaultdict(lambda: {"count": 0, "amount": 0.0})
        
        for claim in claims:
            month_key = claim.date_submitted.strftime("%Y-%m")
            monthly_data[month_key]["count"] += 1
            monthly_data[month_key]["amount"] += claim.total_amount
        
        trends = [
            {"month": month, "count": data["count"], "total": data["amount"]}
            for month, data in sorted(monthly_data.items())
        ]
        
        return trends
    
    def _get_top_claimants(self, claims: List[Claim], limit: int = 10) -> List[Dict]:
        """Get top claimants by claim count and amount"""
        claimant_data = defaultdict(lambda: {"count": 0, "total": 0.0})
        
        for claim in claims:
            claimant = claim.claimant_name or "Unknown"
            claimant_data[claimant]["count"] += 1
            claimant_data[claimant]["total"] += claim.total_amount
        
        top_claimants = sorted(
            claimant_data.items(),
            key=lambda x: x[1]["total"],
            reverse=True
        )[:limit]
        
        return [
            {
                "claimant": claimant,
                "count": data["count"],
                "total": data["total"]
            }
            for claimant, data in top_claimants
        ]

