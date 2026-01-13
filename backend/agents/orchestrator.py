"""
Orchestrator Agent - Coordinates workflow between specialized agents
"""
import logging
from typing import Dict, List, Optional, Any
from backend.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class OrchestratorAgent(BaseAgent):
    """Orchestrates multi-agent workflows for claim processing"""
    
    def __init__(self):
        super().__init__(
            agent_name="Orchestrator",
            system_message="You are an orchestrator that coordinates multiple specialized agents to process insurance claims."
        )
        self.agents = {}
        
    def register_agent(self, agent_name: str, agent: BaseAgent):
        """Register an agent for orchestration"""
        self.agents[agent_name] = agent
        self.log_action("agent_registered", {"agent_name": agent_name})
    
    def process(self, input_data: Any, workflow: str = "default", **kwargs) -> Dict[str, Any]:
        """
        Process input through a workflow
        
        Args:
            input_data: Input data (typically a claim document or claim data)
            workflow: Workflow name to execute
            **kwargs: Additional parameters
            
        Returns:
            Processing result with all agent outputs
        """
        self.log_action("workflow_started", {"workflow": workflow})
        
        try:
            if workflow == "process_new_claim":
                return self._process_new_claim_workflow(input_data, **kwargs)
            elif workflow == "validate_and_approve":
                return self._validate_and_approve_workflow(input_data, **kwargs)
            elif workflow == "analyze_patterns":
                return self._analyze_patterns_workflow(input_data, **kwargs)
            else:
                return self._default_workflow(input_data, **kwargs)
        except Exception as e:
            return self.handle_error(e, {"workflow": workflow})
    
    def _process_new_claim_workflow(self, input_data: Dict, **kwargs) -> Dict[str, Any]:
        """Full claim processing pipeline"""
        result = {
            "workflow": "process_new_claim",
            "steps": [],
            "final_result": None
        }
        
        # Step 1: OCR processing
        if "ocr_agent" in self.agents and "document" in input_data:
            ocr_result = self.agents["ocr_agent"].process(input_data["document"], **kwargs)
            result["steps"].append({"step": "ocr", "result": ocr_result})
            input_data["ocr_text"] = ocr_result.get("text", "")
            input_data["ocr_layout"] = ocr_result.get("layout", [])
        
        # Step 2: Extraction
        if "extraction_agent" in self.agents:
            extraction_result = self.agents["extraction_agent"].process(input_data, **kwargs)
            result["steps"].append({"step": "extraction", "result": extraction_result})
            input_data["extracted_data"] = extraction_result.get("data", {})
        
        # Step 3: Duplicate detection
        if "duplicate_agent" in self.agents:
            duplicate_result = self.agents["duplicate_agent"].process(input_data, **kwargs)
            result["steps"].append({"step": "duplicate_detection", "result": duplicate_result})
            input_data["duplicate_matches"] = duplicate_result.get("matches", [])
        
        # Step 4: Validation
        if "validation_agent" in self.agents:
            validation_result = self.agents["validation_agent"].process(input_data, **kwargs)
            result["steps"].append({"step": "validation", "result": validation_result})
            input_data["validation_results"] = validation_result.get("results", [])
        
        # Step 5: Fraud detection
        if "fraud_detection_agent" in self.agents:
            fraud_result = self.agents["fraud_detection_agent"].process(input_data, **kwargs)
            result["steps"].append({"step": "fraud_detection", "result": fraud_result})
            input_data["fraud_risk"] = fraud_result.get("risk_score", 0.0)
        
        result["final_result"] = input_data
        self.log_action("workflow_completed", {"workflow": "process_new_claim"})
        return result
    
    def _validate_and_approve_workflow(self, input_data: Dict, **kwargs) -> Dict[str, Any]:
        """Validation and approval workflow"""
        result = {
            "workflow": "validate_and_approve",
            "steps": [],
            "approved": False
        }
        
        # Validation
        if "validation_agent" in self.agents:
            validation_result = self.agents["validation_agent"].process(input_data, **kwargs)
            result["steps"].append({"step": "validation", "result": validation_result})
            
            if not validation_result.get("is_valid", False):
                result["approved"] = False
                result["reason"] = "Validation failed"
                return result
        
        # Fraud check
        if "fraud_detection_agent" in self.agents:
            fraud_result = self.agents["fraud_detection_agent"].process(input_data, **kwargs)
            result["steps"].append({"step": "fraud_check", "result": fraud_result})
            
            if fraud_result.get("risk_score", 0.0) > 0.7:
                result["approved"] = False
                result["reason"] = "High fraud risk"
                return result
        
        result["approved"] = True
        return result
    
    def _analyze_patterns_workflow(self, input_data: Dict, **kwargs) -> Dict[str, Any]:
        """Pattern analysis workflow"""
        result = {
            "workflow": "analyze_patterns",
            "steps": [],
            "insights": []
        }
        
        # Analytics
        if "analytics_agent" in self.agents:
            analytics_result = self.agents["analytics_agent"].process(input_data, **kwargs)
            result["steps"].append({"step": "analytics", "result": analytics_result})
            result["insights"] = analytics_result.get("insights", [])
        
        return result
    
    def _default_workflow(self, input_data: Any, **kwargs) -> Dict[str, Any]:
        """Default workflow - simple pass-through"""
        return {
            "workflow": "default",
            "input": input_data,
            "processed": True
        }
