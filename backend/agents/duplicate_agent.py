"""
Duplicate Detection Agent - Identifies duplicate claims using similarity analysis
"""
import logging
from typing import Dict, Any, List, Optional
from backend.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class DuplicateAgent(BaseAgent):
    """Agent for detecting duplicate claims"""
    
    def __init__(self):
        """Initialize Duplicate Detection Agent"""
        super().__init__(
            agent_name="DuplicateDetection",
            system_message="You are a duplicate detection agent that identifies similar or duplicate claims."
        )
        self.log_action("initialized")
    
    def process(self, input_data: Any, **kwargs) -> Dict[str, Any]:
        """
        Detect duplicate claims
        
        Args:
            input_data: Claim data dictionary
            **kwargs: Additional parameters:
                - existing_claims: List of existing claims to compare against
                - similarity_threshold: Float threshold for duplicate detection (default: 0.85)
        
        Returns:
            Dictionary with duplicate detection results:
            - matches: List of duplicate matches with similarity scores
            - highest_similarity: Highest similarity score found
            - is_duplicate: Boolean indicating if duplicates were found
        """
        try:
            # Extract claim data
            if isinstance(input_data, dict):
                claim_data = input_data.get("extracted_data", input_data)
            else:
                return self.handle_error(
                    ValueError("Input must be a dictionary with claim data"),
                    {"input_type": type(input_data).__name__}
                )
            
            existing_claims = kwargs.get("existing_claims", [])
            similarity_threshold = kwargs.get("similarity_threshold", 0.85)
            
            self.log_action("duplicate_detection_started", {
                "claim_id": claim_data.get("id"),
                "existing_claims_count": len(existing_claims)
            })
            
            matches = []
            
            for existing_claim in existing_claims:
                similarity = self._calculate_similarity(claim_data, existing_claim)
                
                if similarity >= similarity_threshold:
                    matches.append({
                        "claim_id": existing_claim.get("id"),
                        "claim_number": existing_claim.get("claim_number"),
                        "similarity_score": similarity,
                        "similar_fields": self._identify_similar_fields(claim_data, existing_claim)
                    })
            
            # Sort by similarity (highest first)
            matches.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            highest_similarity = matches[0]["similarity_score"] if matches else 0.0
            
            result = {
                "success": True,
                "matches": matches,
                "highest_similarity": highest_similarity,
                "is_duplicate": len(matches) > 0,
                "match_count": len(matches)
            }
            
            self.log_action("duplicate_detection_completed", {
                "match_count": len(matches),
                "highest_similarity": highest_similarity
            })
            
            return result
            
        except Exception as e:
            return self.handle_error(e, {"input_type": type(input_data).__name__})
    
    def _calculate_similarity(self, claim1: Dict, claim2: Dict) -> float:
        """
        Calculate similarity between two claims
        
        Args:
            claim1: First claim data
            claim2: Second claim data
        
        Returns:
            Similarity score between 0.0 and 1.0
        """
        score = 0.0
        factors = 0
        
        # Claimant name similarity (weight: 0.25)
        name1 = str(claim1.get("claimant_name", "")).lower().strip()
        name2 = str(claim2.get("claimant_name", "")).lower().strip()
        if name1 and name2:
            name_sim = self._string_similarity(name1, name2)
            score += name_sim * 0.25
            factors += 0.25
        
        # Amount similarity (weight: 0.30)
        amount1 = float(claim1.get("total_amount", 0))
        amount2 = float(claim2.get("total_amount", 0))
        if amount1 > 0 and amount2 > 0:
            amount_diff = abs(amount1 - amount2)
            amount_avg = (amount1 + amount2) / 2
            if amount_avg > 0:
                amount_sim = max(0, 1 - (amount_diff / amount_avg))
                score += amount_sim * 0.30
                factors += 0.30
        
        # Date similarity (weight: 0.25)
        date1 = claim1.get("date_of_incident")
        date2 = claim2.get("date_of_incident")
        if date1 and date2:
            try:
                from datetime import datetime
                if isinstance(date1, str):
                    date1 = datetime.fromisoformat(date1.split("T")[0])
                if isinstance(date2, str):
                    date2 = datetime.fromisoformat(date2.split("T")[0])
                
                date_diff = abs((date1 - date2).days)
                date_sim = max(0, 1 - (date_diff / 7.0))  # 7 day tolerance
                score += date_sim * 0.25
                factors += 0.25
            except:
                pass
        
        # Claim type similarity (weight: 0.20)
        type1 = claim1.get("claim_type", "")
        type2 = claim2.get("claim_type", "")
        if type1 and type2 and type1 == type2:
            score += 0.20
            factors += 0.20
        
        return score / factors if factors > 0 else 0.0
    
    def _string_similarity(self, s1: str, s2: str) -> float:
        """Calculate string similarity"""
        if s1 == s2:
            return 1.0
        
        if s1 in s2 or s2 in s1:
            return 0.8
        
        # Character overlap
        set1 = set(s1.lower())
        set2 = set(s2.lower())
        if len(set1) == 0 and len(set2) == 0:
            return 1.0
        if len(set1) == 0 or len(set2) == 0:
            return 0.0
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0
    
    def _identify_similar_fields(self, claim1: Dict, claim2: Dict) -> List[str]:
        """Identify which fields are similar between two claims"""
        similar_fields = []
        
        # Check name
        name1 = str(claim1.get("claimant_name", "")).lower().strip()
        name2 = str(claim2.get("claimant_name", "")).lower().strip()
        if name1 and name2 and self._string_similarity(name1, name2) > 0.7:
            similar_fields.append("claimant_name")
        
        # Check amount (within 5%)
        amount1 = float(claim1.get("total_amount", 0))
        amount2 = float(claim2.get("total_amount", 0))
        if amount1 > 0 and amount2 > 0:
            diff = abs(amount1 - amount2) / max(amount1, amount2)
            if diff < 0.05:
                similar_fields.append("total_amount")
        
        # Check date (within 7 days)
        date1 = claim1.get("date_of_incident")
        date2 = claim2.get("date_of_incident")
        if date1 and date2:
            try:
                from datetime import datetime
                if isinstance(date1, str):
                    date1 = datetime.fromisoformat(date1.split("T")[0])
                if isinstance(date2, str):
                    date2 = datetime.fromisoformat(date2.split("T")[0])
                
                date_diff = abs((date1 - date2).days)
                if date_diff <= 7:
                    similar_fields.append("date_of_incident")
            except:
                pass
        
        # Check claim type
        if claim1.get("claim_type") == claim2.get("claim_type"):
            similar_fields.append("claim_type")
        
        return similar_fields
