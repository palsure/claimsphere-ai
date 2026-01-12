"""
Agent Coordinator Service - Manages agent lifecycle and communication
"""
import logging
from typing import Dict, Optional, Any
from backend.agents import (
    OrchestratorAgent,
    OCRAgent,
    ExtractionAgent,
    ValidationAgent,
    FraudDetectionAgent,
    DuplicateAgent,
    QueryAgent,
    AnalyticsAgent
)
from backend.ocr_processor import OCRProcessor

logger = logging.getLogger(__name__)


class AgentCoordinator:
    """Manages agent lifecycle, communication, and coordination"""
    
    def __init__(self):
        """Initialize agent coordinator"""
        self.orchestrator = None
        self.agents = {}
        self._initialized = False
        logger.info("Agent Coordinator initialized")
    
    def initialize(self, ocr_processor: Optional[OCRProcessor] = None):
        """
        Initialize all agents
        
        Args:
            ocr_processor: Optional OCRProcessor instance (will create one if not provided)
        """
        if self._initialized:
            logger.warning("Agents already initialized")
            return
        
        try:
            # Create orchestrator
            self.orchestrator = OrchestratorAgent()
            
            # Create and register agents
            ocr_agent = OCRAgent(ocr_processor=ocr_processor)
            self.orchestrator.register_agent("ocr_agent", ocr_agent)
            self.agents["ocr"] = ocr_agent
            
            extraction_agent = ExtractionAgent()
            self.orchestrator.register_agent("extraction_agent", extraction_agent)
            self.agents["extraction"] = extraction_agent
            
            validation_agent = ValidationAgent()
            self.orchestrator.register_agent("validation_agent", validation_agent)
            self.agents["validation"] = validation_agent
            
            fraud_agent = FraudDetectionAgent()
            self.orchestrator.register_agent("fraud_detection_agent", fraud_agent)
            self.agents["fraud"] = fraud_agent
            
            duplicate_agent = DuplicateAgent()
            self.orchestrator.register_agent("duplicate_agent", duplicate_agent)
            self.agents["duplicate"] = duplicate_agent
            
            query_agent = QueryAgent()
            self.orchestrator.register_agent("query_agent", query_agent)
            self.agents["query"] = query_agent
            
            analytics_agent = AnalyticsAgent()
            self.orchestrator.register_agent("analytics_agent", analytics_agent)
            self.agents["analytics"] = analytics_agent
            
            self._initialized = True
            logger.info("All agents initialized and registered")
            
        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}", exc_info=True)
            raise
    
    def get_agent(self, agent_name: str) -> Optional[Any]:
        """
        Get an agent by name
        
        Args:
            agent_name: Name of the agent (ocr, extraction, validation, fraud, duplicate, query, analytics)
        
        Returns:
            Agent instance or None if not found
        """
        if not self._initialized:
            self.initialize()
        
        return self.agents.get(agent_name)
    
    def get_orchestrator(self) -> OrchestratorAgent:
        """Get the orchestrator agent"""
        if not self._initialized:
            self.initialize()
        
        return self.orchestrator
    
    def process_claim(self, claim_data: Dict, workflow: str = "process_new_claim", **kwargs) -> Dict[str, Any]:
        """
        Process a claim through the orchestrator
        
        Args:
            claim_data: Claim data dictionary
            workflow: Workflow name to execute
            **kwargs: Additional parameters
        
        Returns:
            Processing result from orchestrator
        """
        if not self._initialized:
            self.initialize()
        
        return self.orchestrator.process(claim_data, workflow=workflow, **kwargs)
    
    def extract_claim_info(self, ocr_text: str, **kwargs) -> Dict[str, Any]:
        """
        Extract claim information using extraction agent
        
        Args:
            ocr_text: OCR text from document
            **kwargs: Additional parameters
        
        Returns:
            Extraction result
        """
        extraction_agent = self.get_agent("extraction")
        if not extraction_agent:
            return {"success": False, "error": "Extraction agent not available"}
        
        return extraction_agent.process(ocr_text, **kwargs)
    
    def validate_claim(self, claim_data: Dict, **kwargs) -> Dict[str, Any]:
        """
        Validate a claim using validation agent
        
        Args:
            claim_data: Claim data dictionary
            **kwargs: Additional parameters
        
        Returns:
            Validation result
        """
        validation_agent = self.get_agent("validation")
        if not validation_agent:
            return {"success": False, "error": "Validation agent not available"}
        
        return validation_agent.process(claim_data, **kwargs)
    
    def detect_fraud(self, claim_data: Dict, **kwargs) -> Dict[str, Any]:
        """
        Detect fraud using fraud detection agent
        
        Args:
            claim_data: Claim data dictionary
            **kwargs: Additional parameters
        
        Returns:
            Fraud detection result
        """
        fraud_agent = self.get_agent("fraud")
        if not fraud_agent:
            return {"success": False, "error": "Fraud detection agent not available"}
        
        return fraud_agent.process(claim_data, **kwargs)
    
    def detect_duplicates(self, claim_data: Dict, existing_claims: list, **kwargs) -> Dict[str, Any]:
        """
        Detect duplicates using duplicate agent
        
        Args:
            claim_data: Claim data dictionary
            existing_claims: List of existing claims to compare against
            **kwargs: Additional parameters
        
        Returns:
            Duplicate detection result
        """
        duplicate_agent = self.get_agent("duplicate")
        if not duplicate_agent:
            return {"success": False, "error": "Duplicate detection agent not available"}
        
        return duplicate_agent.process(claim_data, existing_claims=existing_claims, **kwargs)
    
    def answer_query(self, query: str, claims_context: list, **kwargs) -> Dict[str, Any]:
        """
        Answer a natural language query using query agent
        
        Args:
            query: Natural language query
            claims_context: List of claims for context
            **kwargs: Additional parameters
        
        Returns:
            Query response
        """
        query_agent = self.get_agent("query")
        if not query_agent:
            return {"success": False, "error": "Query agent not available"}
        
        return query_agent.process(query, claims_context=claims_context, **kwargs)
    
    def generate_analytics(self, claims: list, analysis_type: str = "summary", **kwargs) -> Dict[str, Any]:
        """
        Generate analytics using analytics agent
        
        Args:
            claims: List of claim dictionaries
            analysis_type: Type of analysis (summary, trends, recommendations)
            **kwargs: Additional parameters
        
        Returns:
            Analytics result
        """
        analytics_agent = self.get_agent("analytics")
        if not analytics_agent:
            return {"success": False, "error": "Analytics agent not available"}
        
        return analytics_agent.process(claims, analysis_type=analysis_type, **kwargs)


# Global coordinator instance
_coordinator: Optional[AgentCoordinator] = None


def get_agent_coordinator() -> AgentCoordinator:
    """Get or create the global agent coordinator instance"""
    global _coordinator
    if _coordinator is None:
        _coordinator = AgentCoordinator()
    return _coordinator
