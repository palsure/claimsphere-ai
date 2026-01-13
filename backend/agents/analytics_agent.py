"""
Analytics Agent - Generates insights, trends, and reports using ERNIE 5.0 Thinking
"""
import os
import json
import logging
from typing import Dict, Any, Optional, List
from backend.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

try:
    from camel.agents import ChatAgent
    from camel.configs import QianfanConfig
    from camel.models import ModelFactory
    from camel.types import ModelPlatformType, ModelType
    from camel.messages import BaseMessage
    CAMEL_AVAILABLE = True
except ImportError:
    CAMEL_AVAILABLE = False
    logger.warning("CAMEL-AI not available. Analytics Agent will use fallback mode.")


class AnalyticsAgent(BaseAgent):
    """Agent for generating analytics, insights, and reports using ERNIE 5.0 Thinking"""
    
    def __init__(self):
        """Initialize Analytics Agent"""
        super().__init__(
            agent_name="Analytics",
            system_message="You are an analytics expert. Generate insights, identify trends, and create comprehensive reports about insurance claims. Provide clear reasoning for your analysis."
        )
        
        self.agent = None
        self._initialize_agent()
        self.log_action("initialized")
    
    def _initialize_agent(self):
        """Initialize CAMEL-AI agent with ERNIE 5.0 Thinking"""
        if not CAMEL_AVAILABLE:
            logger.warning("CAMEL-AI not available. Analytics Agent will use fallback.")
            return
        
        try:
            qianfan_api_key = os.getenv('QIANFAN_API_KEY')
            if not qianfan_api_key:
                logger.warning("QIANFAN_API_KEY not set. Analytics Agent will use fallback.")
                return
            
            model = ModelFactory.create(
                model_platform=ModelPlatformType.QIANFAN,
                model_type=ModelType.ERNIE_5_0_THINKING,
                model_config_dict=QianfanConfig(temperature=0.3).as_dict(),  # Slightly higher temp for creativity
            )
            
            self.agent = ChatAgent(
                system_message=self.system_message,
                model=model
            )
            
            logger.info("Analytics Agent initialized with ERNIE 5.0 Thinking")
        except Exception as e:
            logger.error(f"Failed to initialize CAMEL-AI agent: {e}", exc_info=True)
    
    def process(self, input_data: Any, **kwargs) -> Dict[str, Any]:
        """
        Generate analytics and insights
        
        Args:
            input_data: Claims data or analytics request
            **kwargs: Additional parameters:
                - claims: List of claim dictionaries
                - analysis_type: Type of analysis (summary, trends, recommendations, etc.)
        
        Returns:
            Dictionary with analytics results:
            - insights: List of insights
            - summary: Summary text
            - trends: Identified trends
            - recommendations: Recommendations
            - reasoning: Reasoning trace from ERNIE 5.0 Thinking
        """
        try:
            # Extract claims data
            if isinstance(input_data, list):
                claims = input_data
            elif isinstance(input_data, dict):
                claims = input_data.get("claims", [])
            else:
                return self.handle_error(
                    ValueError("Input must be a list of claims or dict with 'claims' key"),
                    {"input_type": type(input_data).__name__}
                )
            
            analysis_type = kwargs.get("analysis_type", "summary")
            
            self.log_action("analytics_started", {
                "claims_count": len(claims),
                "analysis_type": analysis_type
            })
            
            # Use CAMEL-AI agent if available
            if self.agent:
                try:
                    result = self._ai_analytics(claims, analysis_type)
                    return result
                except Exception as e:
                    logger.error(f"AI analytics failed: {e}", exc_info=True)
                    # Fallback to basic analytics
                    return self._basic_analytics(claims, analysis_type)
            else:
                # Fallback to basic analytics
                return self._basic_analytics(claims, analysis_type)
                
        except Exception as e:
            return self.handle_error(e, {"input_type": type(input_data).__name__})
    
    def _ai_analytics(self, claims: List[Dict], analysis_type: str) -> Dict[str, Any]:
        """Generate analytics using CAMEL-AI agent"""
        claims_json = json.dumps(claims, indent=2, default=str)
        
        if analysis_type == "summary":
            prompt = f"""Generate a concise summary of these claims in natural language:

{claims_json}

Include:
- Total claims and amounts
- Status breakdown
- Claim types
- Notable trends
- Any recommendations

Keep it under 200 words."""
        elif analysis_type == "trends":
            prompt = f"""Analyze these claims and identify trends:

{claims_json}

Identify:
- Spending trends over time
- Most common claim types
- Status patterns
- Amount distributions
- Any anomalies or patterns

Provide detailed analysis with reasoning."""
        elif analysis_type == "recommendations":
            prompt = f"""Based on these claims, provide recommendations:

{claims_json}

Provide:
- Process improvement recommendations
- Risk management suggestions
- Efficiency opportunities
- Quality improvement ideas

Be specific and actionable."""
        else:
            prompt = f"""Analyze these claims comprehensively:

{claims_json}

Provide insights, trends, and recommendations."""
        
        user_message = BaseMessage.make_user_message(
            role_name="User",
            content=prompt
        )
        response = self.agent.step(user_message)
        
        # Extract reasoning and content
        reasoning = ""
        if hasattr(response.msgs[0], 'reasoning_content') and response.msgs[0].reasoning_content:
            reasoning = response.msgs[0].reasoning_content
        
        analysis_text = response.msgs[0].content
        
        # Parse insights from the response
        insights = self._extract_insights(analysis_text, claims)
        
        return {
            "success": True,
            "summary": analysis_text,
            "insights": insights,
            "reasoning": reasoning,
            "analysis_type": analysis_type,
            "claims_analyzed": len(claims),
            "method": "ERNIE_5_0_Thinking"
        }
    
    def _basic_analytics(self, claims: List[Dict], analysis_type: str) -> Dict[str, Any]:
        """Generate basic analytics without AI"""
        if not claims:
            return {
                "success": True,
                "summary": "No claims available for analysis.",
                "insights": [],
                "method": "Basic"
            }
        
        # Calculate basic statistics
        total_claims = len(claims)
        total_amount = sum(c.get("total_amount", 0) for c in claims)
        avg_amount = total_amount / total_claims if total_claims > 0 else 0
        
        # Status breakdown
        status_counts = {}
        for c in claims:
            status = c.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Type breakdown
        type_counts = {}
        for c in claims:
            claim_type = c.get("claim_type", "other")
            type_counts[claim_type] = type_counts.get(claim_type, 0) + 1
        
        summary = f"""Claims Analytics Summary:

Total Claims: {total_claims}
Total Amount: ${total_amount:,.2f}
Average Amount: ${avg_amount:,.2f}

Status Breakdown:
{json.dumps(status_counts, indent=2)}

Claim Types:
{json.dumps(type_counts, indent=2)}"""
        
        insights = [
            f"Total of {total_claims} claims processed",
            f"Average claim amount: ${avg_amount:,.2f}",
            f"Most common status: {max(status_counts.items(), key=lambda x: x[1])[0] if status_counts else 'N/A'}"
        ]
        
        return {
            "success": True,
            "summary": summary,
            "insights": insights,
            "analysis_type": analysis_type,
            "claims_analyzed": total_claims,
            "method": "Basic"
        }
    
    def _extract_insights(self, analysis_text: str, claims: List[Dict]) -> List[str]:
        """Extract key insights from analysis text"""
        insights = []
        
        # Simple extraction: look for bullet points or numbered items
        lines = analysis_text.split("\n")
        for line in lines:
            line = line.strip()
            if line and (line.startswith("-") or line.startswith("•") or line.startswith("*") or 
                        (len(line) > 0 and line[0].isdigit() and "." in line[:3])):
                insight = line.lstrip("-•*0123456789. ").strip()
                if insight:
                    insights.append(insight)
        
        # If no structured insights found, create from summary
        if not insights and analysis_text:
            # Split into sentences and take key ones
            sentences = [s.strip() for s in analysis_text.split(".") if s.strip()]
            insights = sentences[:5]  # Take first 5 sentences
        
        return insights
