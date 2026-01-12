"""
Multi-Agent System for ClaimSphere AI

This module implements a comprehensive multi-agent system using CAMEL-AI framework
to tackle complex claim processing workflows.
"""

from backend.agents.base_agent import BaseAgent
from backend.agents.orchestrator import OrchestratorAgent
from backend.agents.ocr_agent import OCRAgent
from backend.agents.extraction_agent import ExtractionAgent
from backend.agents.validation_agent import ValidationAgent
from backend.agents.fraud_detection_agent import FraudDetectionAgent
from backend.agents.duplicate_agent import DuplicateAgent
from backend.agents.query_agent import QueryAgent
from backend.agents.analytics_agent import AnalyticsAgent
from backend.agents.review_agent import ReviewAgent
from backend.agents.approval_agent import ApprovalAgent
from backend.agents.role_playing_coordinator import RolePlayingCoordinator

__all__ = [
    "BaseAgent",
    "OrchestratorAgent",
    "OCRAgent",
    "ExtractionAgent",
    "ValidationAgent",
    "FraudDetectionAgent",
    "DuplicateAgent",
    "QueryAgent",
    "AnalyticsAgent",
    "ReviewAgent",
    "ApprovalAgent",
    "RolePlayingCoordinator",
]
