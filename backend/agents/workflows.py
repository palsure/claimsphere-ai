"""
Multi-Agent Workflows - Complex workflows for claim processing
"""
import logging
from typing import Dict, Any, List, Optional
from backend.services.agent_coordinator import get_agent_coordinator

logger = logging.getLogger(__name__)


def process_new_claim_workflow(
    document: Any,
    existing_claims: Optional[List[Dict]] = None,
    validation_rules: Optional[List[Dict]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Full claim processing workflow
    
    This workflow processes a new claim through the complete pipeline:
    1. OCR extraction
    2. Data extraction
    3. Duplicate detection
    4. Validation
    5. Fraud detection
    
    Args:
        document: Document file (path, bytes, or dict)
        existing_claims: List of existing claims for duplicate detection
        validation_rules: List of validation rules to apply
        **kwargs: Additional parameters
    
    Returns:
        Complete processing result with all agent outputs
    """
    coordinator = get_agent_coordinator()
    orchestrator = coordinator.get_orchestrator()
    
    # Prepare input data
    input_data = {
        "document": document,
        "existing_claims": existing_claims or [],
        "validation_rules": validation_rules or []
    }
    
    # Process through orchestrator
    result = orchestrator.process(
        input_data,
        workflow="process_new_claim",
        existing_claims=existing_claims,
        validation_rules=validation_rules,
        **kwargs
    )
    
    return result


def validate_and_approve_workflow(
    claim_data: Dict,
    validation_rules: Optional[List[Dict]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Validation and approval workflow
    
    This workflow validates a claim and determines if it can be auto-approved:
    1. Validation
    2. Fraud check
    3. Approval decision
    
    Args:
        claim_data: Claim data dictionary
        validation_rules: List of validation rules
        **kwargs: Additional parameters
    
    Returns:
        Validation and approval result
    """
    coordinator = get_agent_coordinator()
    orchestrator = coordinator.get_orchestrator()
    
    input_data = {
        "extracted_data": claim_data,
        "validation_rules": validation_rules or []
    }
    
    result = orchestrator.process(
        input_data,
        workflow="validate_and_approve",
        validation_rules=validation_rules,
        **kwargs
    )
    
    return result


def analyze_claim_patterns_workflow(
    claims: List[Dict],
    analysis_type: str = "summary",
    **kwargs
) -> Dict[str, Any]:
    """
    Pattern analysis workflow
    
    This workflow analyzes claim patterns and generates insights:
    1. Analytics generation
    2. Trend identification
    3. Recommendations
    
    Args:
        claims: List of claim dictionaries
        analysis_type: Type of analysis (summary, trends, recommendations)
        **kwargs: Additional parameters
    
    Returns:
        Analytics result with insights
    """
    coordinator = get_agent_coordinator()
    orchestrator = coordinator.get_orchestrator()
    
    input_data = {
        "claims": claims
    }
    
    result = orchestrator.process(
        input_data,
        workflow="analyze_patterns",
        analysis_type=analysis_type,
        **kwargs
    )
    
    return result


def quick_extraction_workflow(
    ocr_text: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Quick extraction workflow (OCR + Extraction only)
    
    Args:
        ocr_text: OCR text from document
        **kwargs: Additional parameters
    
    Returns:
        Extraction result
    """
    coordinator = get_agent_coordinator()
    extraction_agent = coordinator.get_agent("extraction")
    
    if not extraction_agent:
        return {"success": False, "error": "Extraction agent not available"}
    
    return extraction_agent.process(ocr_text, **kwargs)


def query_workflow(
    query: str,
    claims_context: List[Dict],
    scope_description: str = "available claims",
    **kwargs
) -> Dict[str, Any]:
    """
    Query workflow for natural language queries
    
    Args:
        query: Natural language query
        claims_context: List of claims for context
        scope_description: Description of data scope (for RBAC)
        **kwargs: Additional parameters
    
    Returns:
        Query response with reasoning
    """
    coordinator = get_agent_coordinator()
    query_agent = coordinator.get_agent("query")
    
    if not query_agent:
        return {"success": False, "error": "Query agent not available"}
    
    return query_agent.process(
        query,
        claims_context=claims_context,
        scope_description=scope_description,
        **kwargs
    )
