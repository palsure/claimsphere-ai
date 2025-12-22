"""Natural Language Query API routes with RBAC enforcement"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_

from backend.database.config import get_db
from backend.database.models import User, Claim, ClaimStatus, RoleType
from backend.auth.dependencies import get_current_user
from backend.api.schemas import NaturalLanguageQuery, QueryResponse
from backend.ernie_service import ErnieService

router = APIRouter()

ernie_service = ErnieService()


@router.post("", response_model=QueryResponse)
async def natural_language_query(
    query_data: NaturalLanguageQuery,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Answer natural language questions about claims with RBAC enforcement.
    
    - USER: Can only query their own claims
    - AGENT: Can query claims assigned to them or in pending review
    - ADMIN: Can query all claims
    
    Responses must cite claim IDs and fields used.
    """
    user_roles = [ur.role.name for ur in current_user.roles]
    
    # Build base query with RBAC filtering
    claims_query = db.query(Claim)
    
    if RoleType.ADMIN in user_roles:
        # Admin can query all claims
        scope_description = "all claims in the system"
    elif RoleType.AGENT in user_roles:
        # Agent can query assigned claims or pending review
        claims_query = claims_query.filter(
            (Claim.assigned_agent_id == current_user.id) |
            (Claim.status == ClaimStatus.PENDING_REVIEW)
        )
        scope_description = "claims assigned to you or pending review"
    else:
        # User can only query own claims
        claims_query = claims_query.filter(Claim.user_id == current_user.id)
        scope_description = "your own claims"
    
    # Apply date filters if provided
    if query_data.date_from:
        claims_query = claims_query.filter(Claim.created_at >= query_data.date_from)
    if query_data.date_to:
        claims_query = claims_query.filter(Claim.created_at <= query_data.date_to)
    if query_data.claim_type:
        claims_query = claims_query.filter(Claim.category == query_data.claim_type)
    if query_data.status:
        claims_query = claims_query.filter(Claim.status == query_data.status)
    
    # Get claims for context
    claims = claims_query.order_by(Claim.created_at.desc()).limit(50).all()
    
    if not claims:
        return QueryResponse(
            query=query_data.query,
            answer=f"No claims found within your access scope ({scope_description}). Please submit a claim first or adjust your filters.",
            claims_analyzed=0,
            cited_claims=[],
            fields_used=[]
        )
    
    # Convert claims to context format
    claims_context = []
    for claim in claims:
        claims_context.append({
            "claim_id": claim.id,
            "claim_number": claim.claim_number,
            "status": claim.status.value,
            "category": claim.category.value,
            "total_amount": claim.total_amount,
            "approved_amount": claim.approved_amount,
            "currency": claim.currency,
            "service_date": claim.service_date.isoformat() if claim.service_date else None,
            "provider_name": claim.provider_name,
            "created_at": claim.created_at.isoformat(),
            "submitted_at": claim.submitted_at.isoformat() if claim.submitted_at else None
        })
    
    # Build prompt with RBAC context
    prompt = f"""You are a claim processing assistant. Answer the user's question about claims.

IMPORTANT RULES:
1. Only use information from the provided claims data - do not make up information
2. Always cite the claim_number when referring to specific claims
3. For aggregate questions, list the claim_numbers used in the calculation
4. If the question cannot be answered from the data, say so clearly
5. The user can only see {scope_description}

CLAIMS DATA (JSON):
{claims_context}

USER QUESTION: {query_data.query}

Provide a clear, factual answer. At the end, list:
- CITED_CLAIMS: [comma-separated list of claim_numbers used]
- FIELDS_USED: [comma-separated list of fields used like total_amount, status, etc.]"""

    try:
        # Call ERNIE for answer
        messages = [{"role": "user", "content": prompt}]
        response = ernie_service.call_ernie_api(messages)
        answer_text = response.get("result", "")
        
        # Parse cited claims and fields from response
        cited_claims = []
        fields_used = []
        
        # Extract CITED_CLAIMS if present
        if "CITED_CLAIMS:" in answer_text:
            try:
                cited_part = answer_text.split("CITED_CLAIMS:")[1].split("\n")[0]
                cited_claims = [c.strip().strip("[]") for c in cited_part.split(",") if c.strip()]
            except:
                pass
        
        # Extract FIELDS_USED if present
        if "FIELDS_USED:" in answer_text:
            try:
                fields_part = answer_text.split("FIELDS_USED:")[1].split("\n")[0]
                fields_used = [f.strip().strip("[]") for f in fields_part.split(",") if f.strip()]
            except:
                pass
        
        # Clean up answer text (remove the citations section)
        clean_answer = answer_text
        if "CITED_CLAIMS:" in clean_answer:
            clean_answer = clean_answer.split("CITED_CLAIMS:")[0].strip()
        
        return QueryResponse(
            query=query_data.query,
            answer=clean_answer,
            claims_analyzed=len(claims),
            cited_claims=cited_claims,
            fields_used=fields_used
        )
        
    except Exception as e:
        # Fallback: provide basic statistics
        return QueryResponse(
            query=query_data.query,
            answer=_generate_fallback_answer(query_data.query, claims),
            claims_analyzed=len(claims),
            cited_claims=[c.claim_number for c in claims[:5]],
            fields_used=["total_amount", "status", "category"]
        )


def _generate_fallback_answer(query: str, claims: List[Claim]) -> str:
    """Generate a basic statistical answer when ERNIE is unavailable"""
    query_lower = query.lower()
    
    total_claims = len(claims)
    total_amount = sum(c.total_amount for c in claims)
    
    # Count by status
    status_counts = {}
    for c in claims:
        status = c.status.value
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Count by category
    category_counts = {}
    category_amounts = {}
    for c in claims:
        cat = c.category.value
        category_counts[cat] = category_counts.get(cat, 0) + 1
        category_amounts[cat] = category_amounts.get(cat, 0) + c.total_amount
    
    # Generate response based on query keywords
    if any(word in query_lower for word in ["total", "sum", "amount"]):
        return f"Based on {total_claims} claims, the total amount is ${total_amount:,.2f}. Status breakdown: {status_counts}"
    
    if any(word in query_lower for word in ["pending", "review", "waiting"]):
        pending = status_counts.get("pending_review", 0) + status_counts.get("submitted", 0)
        return f"There are {pending} claims pending review out of {total_claims} total claims."
    
    if any(word in query_lower for word in ["approved", "approval"]):
        approved = status_counts.get("approved", 0) + status_counts.get("auto_approved", 0)
        approved_amount = sum(c.approved_amount or 0 for c in claims if c.status.value in ["approved", "auto_approved"])
        return f"{approved} claims have been approved for a total of ${approved_amount:,.2f}."
    
    if any(word in query_lower for word in ["denied", "rejected"]):
        denied = status_counts.get("denied", 0)
        return f"{denied} claims have been denied out of {total_claims} total claims."
    
    if any(word in query_lower for word in ["category", "type", "breakdown"]):
        breakdown = ", ".join([f"{k}: {v} (${category_amounts[k]:,.2f})" for k, v in category_counts.items()])
        return f"Claims by category: {breakdown}"
    
    # Default summary
    return f"""Claims Summary (based on {total_claims} claims):
• Total amount: ${total_amount:,.2f}
• Status: {', '.join([f'{k}: {v}' for k, v in status_counts.items()])}
• Categories: {', '.join([f'{k}: {v}' for k, v in category_counts.items()])}

Note: For more detailed analysis, please ensure your ERNIE API credentials are configured correctly."""

