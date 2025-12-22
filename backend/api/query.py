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


def _format_status(status: str) -> str:
    """Format status value for display"""
    status_labels = {
        "pending_review": "Pending Review",
        "submitted": "Submitted",
        "extracted": "Processing",
        "validated": "Validated",
        "approved": "Approved",
        "auto_approved": "Auto-Approved",
        "denied": "Denied",
        "pended": "On Hold",
        "draft": "Draft"
    }
    return status_labels.get(status, status.replace("_", " ").title())


def _format_category(category: str) -> str:
    """Format category value for display"""
    return category.replace("_", " ").title()


def _generate_fallback_answer(query: str, claims: List[Claim]) -> str:
    """Generate a basic statistical answer when ERNIE is unavailable"""
    query_lower = query.lower()
    
    total_claims = len(claims)
    total_amount = sum(c.total_amount or 0 for c in claims)
    avg_amount = total_amount / total_claims if total_claims > 0 else 0
    
    # Count by status
    status_counts = {}
    for c in claims:
        status = c.status.value
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Count by category
    category_counts = {}
    category_amounts = {}
    for c in claims:
        cat = c.category.value if c.category else "uncategorized"
        category_counts[cat] = category_counts.get(cat, 0) + 1
        category_amounts[cat] = category_amounts.get(cat, 0) + (c.total_amount or 0)
    
    # Format status breakdown nicely
    def format_status_breakdown():
        lines = []
        for status, count in sorted(status_counts.items(), key=lambda x: -x[1]):
            lines.append(f"• {_format_status(status)}: {count} claim{'s' if count != 1 else ''}")
        return "\n".join(lines)
    
    # Format category breakdown nicely
    def format_category_breakdown():
        lines = []
        for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
            amount = category_amounts.get(cat, 0)
            lines.append(f"• {_format_category(cat)}: {count} claim{'s' if count != 1 else ''} (${amount:,.2f})")
        return "\n".join(lines)
    
    # Generate response based on query keywords
    if any(word in query_lower for word in ["total", "sum", "amount"]):
        response = f"""📊 Claims Financial Summary

Total Claims: {total_claims}
Total Amount: ${total_amount:,.2f}
Average Amount: ${avg_amount:,.2f}

Status Breakdown:
{format_status_breakdown()}"""
        return response
    
    if any(word in query_lower for word in ["pending", "review", "waiting"]):
        pending = status_counts.get("pending_review", 0) + status_counts.get("submitted", 0) + status_counts.get("extracted", 0)
        pending_amount = sum(c.total_amount or 0 for c in claims if c.status.value in ["pending_review", "submitted", "extracted"])
        return f"""⏳ Pending Claims Summary

Pending Claims: {pending} out of {total_claims} total
Pending Amount: ${pending_amount:,.2f}

These claims are awaiting review or processing."""
    
    if any(word in query_lower for word in ["approved", "approval"]):
        approved = status_counts.get("approved", 0) + status_counts.get("auto_approved", 0)
        approved_amount = sum(c.approved_amount or c.total_amount or 0 for c in claims if c.status.value in ["approved", "auto_approved"])
        approval_rate = (approved / total_claims * 100) if total_claims > 0 else 0
        return f"""✅ Approved Claims Summary

Approved Claims: {approved} out of {total_claims}
Approved Amount: ${approved_amount:,.2f}
Approval Rate: {approval_rate:.1f}%"""
    
    if any(word in query_lower for word in ["denied", "rejected"]):
        denied = status_counts.get("denied", 0)
        denied_amount = sum(c.total_amount or 0 for c in claims if c.status.value == "denied")
        denial_rate = (denied / total_claims * 100) if total_claims > 0 else 0
        return f"""❌ Denied Claims Summary

Denied Claims: {denied} out of {total_claims}
Denied Amount: ${denied_amount:,.2f}
Denial Rate: {denial_rate:.1f}%"""
    
    if any(word in query_lower for word in ["category", "type", "breakdown"]):
        return f"""📁 Claims by Category

{format_category_breakdown()}

Total: {total_claims} claims, ${total_amount:,.2f}"""
    
    if any(word in query_lower for word in ["average", "avg", "mean"]):
        return f"""📈 Claims Statistics

Total Claims: {total_claims}
Total Amount: ${total_amount:,.2f}
Average Amount: ${avg_amount:,.2f}

Highest Category: {max(category_amounts.items(), key=lambda x: x[1])[0].replace('_', ' ').title() if category_amounts else 'N/A'}"""
    
    if any(word in query_lower for word in ["medical", "health", "doctor", "hospital"]):
        medical_claims = [c for c in claims if c.category and "medical" in c.category.value.lower()]
        medical_amount = sum(c.total_amount or 0 for c in medical_claims)
        return f"""🏥 Medical Claims Summary

Medical Claims: {len(medical_claims)}
Total Medical Amount: ${medical_amount:,.2f}"""
    
    # Default comprehensive summary
    return f"""📋 Claims Summary

Overview:
• Total Claims: {total_claims}
• Total Amount: ${total_amount:,.2f}
• Average Amount: ${avg_amount:,.2f}

Status Breakdown:
{format_status_breakdown()}

Categories:
{format_category_breakdown()}

💡 Tip: Try asking specific questions like "How many claims are approved?" or "What's the total pending amount?\""""

