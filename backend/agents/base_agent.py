"""
Base Agent class for all specialized agents in the multi-agent system
"""
import os
import logging
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all agents in the multi-agent system"""
    
    def __init__(self, agent_name: str, system_message: str = ""):
        """
        Initialize base agent
        
        Args:
            agent_name: Name of the agent
            system_message: System message for the agent
        """
        self.agent_name = agent_name
        self.system_message = system_message
        self.logger = logging.getLogger(f"{__name__}.{agent_name}")
        
    def log_action(self, action: str, details: Optional[Dict] = None):
        """Log agent actions for debugging and auditing"""
        log_data = {
            "agent": self.agent_name,
            "action": action,
            "details": details or {}
        }
        self.logger.info(f"Agent {self.agent_name}: {action}", extra=log_data)
    
    def handle_error(self, error: Exception, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Handle errors gracefully
        
        Args:
            error: The exception that occurred
            context: Additional context about the error
            
        Returns:
            Error response dictionary
        """
        error_info = {
            "error": str(error),
            "agent": self.agent_name,
            "context": context or {}
        }
        self.logger.error(f"Error in {self.agent_name}: {error}", exc_info=True, extra=error_info)
        
        return {
            "success": False,
            "error": str(error),
            "agent": self.agent_name
        }
    
    @abstractmethod
    def process(self, input_data: Any, **kwargs) -> Dict[str, Any]:
        """
        Process input data (to be implemented by subclasses)
        
        Args:
            input_data: Input data to process
            **kwargs: Additional parameters
            
        Returns:
            Processing result dictionary
        """
        pass
    
    def validate_input(self, input_data: Any) -> bool:
        """
        Validate input data (can be overridden by subclasses)
        
        Args:
            input_data: Input data to validate
            
        Returns:
            True if valid, False otherwise
        """
        return input_data is not None
