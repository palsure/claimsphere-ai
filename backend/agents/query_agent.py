"""
Query Agent - Natural language queries using CAMEL-AI with OLLAMA (phi3:mini)
"""
import os
import json
import logging
import time
from typing import Dict, Any, Optional, List
from backend.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

try:
    from camel.agents import ChatAgent
    from camel.models import OllamaModel
    from camel.messages import BaseMessage
    CAMEL_AVAILABLE = True
except ImportError:
    CAMEL_AVAILABLE = False
    logger.warning("CAMEL-AI not available. Query Agent will use fallback mode.")


class QueryAgent(BaseAgent):
    """Agent for handling natural language queries using ERNIE 5.0 Thinking"""
    
    def __init__(self):
        """Initialize Query Agent with CAMEL-AI ChatAgent using OLLAMA"""
        super().__init__(
            agent_name="Query",
            system_message="""Answer questions about claims using provided data. Cite claim numbers. End with CITED_CLAIMS: [list] and FIELDS_USED: [list]."""
        )
        
        self.agent = None
        self._initialize_agent()
        if self.agent:
            logger.info("✅ Query Agent initialized with CAMEL-AI")
        else:
            logger.warning("⚠️ Query Agent initialized WITHOUT CAMEL-AI - will use fallback")
        self.log_action("initialized")
    
    def _initialize_agent(self):
        """Initialize CAMEL-AI ChatAgent with OLLAMA (phi3:mini)"""
        if not CAMEL_AVAILABLE:
            logger.warning("CAMEL-AI not available. Query Agent will use fallback.")
            return
        
        use_ollama = os.getenv("USE_OLLAMA", "true").lower() in ("true", "1", "yes")
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
        
        model = None
        ollama_model_name = None

        try:
            if use_ollama and ollama_url:
                try:
                    import requests
                    logger.info(f"Checking OLLAMA availability at {ollama_url}...")
                    response = requests.get(f"{ollama_url}/api/tags", timeout=5)
                    if response.status_code == 200:
                        models = response.json().get('models', [])
                        model_names = [m.get('name', '') for m in models]
                        
                        # Only use phi3 or phi-3 mini
                        if any('phi3:mini' in name.lower() or 'phi-3:mini' in name.lower() for name in model_names):
                            ollama_model_name = 'phi3:mini'
                            logger.info(f"Using {ollama_model_name} (phi3 mini - fastest)")
                        elif any('phi3' in name.lower() or 'phi-3' in name.lower() for name in model_names):
                            for name in model_names:
                                if 'phi3' in name.lower() or 'phi-3' in name.lower():
                                    ollama_model_name = name.split(':')[0] if ':' in name else name
                                    logger.info(f"Using {ollama_model_name} (phi3 model)")
                                    break
                        
                        if ollama_model_name:
                            # Use same configuration as role_playing_coordinator (which works reliably)
                            model = OllamaModel(
                                model_type=ollama_model_name,
                                model_config_dict={
                                    'temperature': 0.2,  # Balanced for quality and speed
                                    'max_tokens': 256  # Same as role_playing_coordinator (proven to work)
                                },
                                url=f'{ollama_url}/v1',  # OpenAI-compatible endpoint
                                timeout=90.0  # Same as role_playing_coordinator (90s works there)
                            )
                            system_message = BaseMessage.make_system_message(
                                role_name="Claim Analytics Assistant",
                                content=self.system_message  # Short system message
                            )
                            self.agent = ChatAgent(
                                system_message=system_message, 
                                model=model,
                                step_timeout=95.0  # Same as role_playing_coordinator (90s + 5s buffer)
                            )
                            logger.info(f"Query Agent initialized with OLLAMA ({ollama_model_name}) via CAMEL-AI")
                            return
                        else:
                            logger.warning("phi3/phi-3 mini model not found in OLLAMA. Query Agent will use fallback.")
                    else:
                        logger.warning(f"OLLAMA returned status {response.status_code}. Query Agent will use fallback.")
                except Exception as e:
                    logger.warning(f"OLLAMA not available at {ollama_url}: {e}. Query Agent will use fallback.")
            
            # If OLLAMA failed or not enabled, model remains None
            if model is None:
                logger.warning("phi3 OLLAMA model not available. Query Agent will use fallback mode.")
                self.agent = None
        except Exception as e:
            logger.error(f"Failed to initialize Query Agent with CAMEL-AI: {e}", exc_info=True)
            self.agent = None
    
    def process(self, input_data: Any, **kwargs) -> Dict[str, Any]:
        """
        Answer natural language query about claims
        
        Args:
            input_data: Query string or dict with 'query' key
            **kwargs: Additional parameters:
                - claims_context: List of claim dictionaries for context
                - scope_description: Description of data scope (for RBAC)
        
        Returns:
            Dictionary with query response:
            - answer: Answer text
            - reasoning: Reasoning trace from ERNIE 5.0 Thinking
            - cited_claims: List of claim numbers cited
            - fields_used: List of fields used in the answer
        """
        try:
            # Extract query
            if isinstance(input_data, str):
                query = input_data
            elif isinstance(input_data, dict):
                query = input_data.get("query", "")
            else:
                return self.handle_error(
                    ValueError("Input must be a query string or dict with 'query' key"),
                    {"input_type": type(input_data).__name__}
                )
            
            if not query or not query.strip():
                return {
                    "success": False,
                    "error": "Query is required",
                    "answer": ""
                }
            
            claims_context = kwargs.get("claims_context", [])
            scope_description = kwargs.get("scope_description", "available claims")
            
            self.log_action("query_processing_started", {
                "query_length": len(query),
                "claims_count": len(claims_context)
            })
            
            # Use CAMEL-AI agent if available
            if self.agent:
                logger.info(f"Using CAMEL-AI Query Agent for query: {query[:50]}...")
                try:
                    result = self._ai_query(query, claims_context, scope_description)
                    logger.info(f"CAMEL-AI query successful. Method: {result.get('method', 'unknown')}")
                    return result
                except Exception as e:
                    logger.error(f"CAMEL-AI query failed: {e}", exc_info=True)
                    logger.warning("Falling back to local answer generator")
                    # Fallback to local answer generator
                    return self._fallback_query(query, claims_context, scope_description)
            else:
                logger.warning("CAMEL-AI agent not initialized. Using local fallback.")
                # Fallback to local answer generator
                return self._fallback_query(query, claims_context, scope_description)
                
        except Exception as e:
            return self.handle_error(e, {"input_type": type(input_data).__name__})
    
    def _ai_query(self, query: str, claims_context: List[Dict], scope_description: str) -> Dict[str, Any]:
        """Process query using CAMEL-AI ChatAgent with OLLAMA"""
        logger.info(f"Processing query with CAMEL-AI: '{query}' (context: {len(claims_context)} claims)")
        
        # Prepare context - limit to most recent 8 claims to reduce token usage
        # Truncate claim data to minimal essential fields only
        essential_claims = []
        for claim in claims_context[-8:]:  # Reduced from 15 to 8
            essential_claim = {
                "id": claim.get("claim_number", "")[:20],  # Short ID
                "s": claim.get("status", ""),  # Short key
                "amt": claim.get("total_amount", 0),  # Short key
                "date": (claim.get("created_at", "") or "")[:10] if claim.get("created_at") else "",  # Just date
            }
            essential_claims.append(essential_claim)
        
        # Use most compact JSON format
        context_summary = json.dumps(essential_claims, default=str, separators=(',', ':'))
        
        # Build prompt that requests concise, relevant answer
        prompt = f"""Q: {query}

Data: {context_summary}

Provide a concise answer with only relevant information:
1. Direct answer to the question (be brief and specific)
2. Key numbers/facts only
3. Brief context if needed

Keep it short and focused. End with:
CITED_CLAIMS: [claim_ids]
FIELDS_USED: [field_names]"""
        
        try:
            logger.info(f"Sending prompt to CAMEL-AI ChatAgent (prompt: {len(prompt)} chars, context: {len(context_summary)} chars)...")
            # Create user message using CAMEL-AI BaseMessage
            user_message = BaseMessage.make_user_message(
                role_name="User",
                content=prompt
            )
            
            # Step through the conversation using ChatAgent with timing
            logger.info("Calling agent.step()...")
            start_time = time.time()
            response = self.agent.step(user_message)
            elapsed = time.time() - start_time
            logger.info(f"Agent.step() completed in {elapsed:.2f} seconds")
            
            # Extract content and reasoning
            answer_text = response.msgs[0].content if response.msgs else ""
            
            # Try to extract reasoning if available (some models provide reasoning_content)
            reasoning = ""
            if hasattr(response.msgs[0], 'reasoning_content') and response.msgs[0].reasoning_content:
                reasoning = response.msgs[0].reasoning_content
                logger.info(f"Extracted reasoning_content (length: {len(reasoning)} chars)")
            
            logger.info(f"Received response from CAMEL-AI (length: {len(answer_text)} chars)")
            
            # Parse cited claims and fields
            cited_claims = []
            fields_used = []
            
            if "CITED_CLAIMS:" in answer_text:
                try:
                    cited_part = answer_text.split("CITED_CLAIMS:")[1].split("\n")[0]
                    # Parse and clean: remove brackets, quotes, and whitespace
                    cited_claims = [
                        c.strip().strip("[]").strip('"').strip("'").strip()
                        for c in cited_part.split(",") 
                        if c.strip()
                    ]
                    logger.info(f"Parsed {len(cited_claims)} cited claims: {cited_claims[:3]}...")
                except Exception as e:
                    logger.warning(f"Failed to parse cited claims: {e}")
            
            if "FIELDS_USED:" in answer_text:
                try:
                    fields_part = answer_text.split("FIELDS_USED:")[1].split("\n")[0]
                    # Parse and clean: remove brackets, quotes, and whitespace
                    fields_used = [
                        f.strip().strip("[]").strip('"').strip("'").strip()
                        for f in fields_part.split(",") 
                        if f.strip()
                    ]
                    logger.info(f"Parsed {len(fields_used)} fields used: {fields_used}")
                except Exception as e:
                    logger.warning(f"Failed to parse fields used: {e}")
            
            # Extract reasoning from answer text if not in reasoning_content
            # Look for reasoning patterns in the response
            if not reasoning:
                # Try to extract reasoning section if present
                reasoning_keywords = ["reasoning:", "analysis:", "explanation:", "because", "since", "based on"]
                lines = answer_text.split("\n")
                reasoning_lines = []
                in_reasoning_section = False
                
                for line in lines:
                    line_lower = line.lower().strip()
                    # Check if this line starts a reasoning section
                    if any(keyword in line_lower for keyword in reasoning_keywords):
                        in_reasoning_section = True
                        reasoning_lines.append(line)
                    elif in_reasoning_section:
                        # Continue collecting reasoning until we hit CITED_CLAIMS or FIELDS_USED
                        if "CITED_CLAIMS:" in line or "FIELDS_USED:" in line:
                            break
                        reasoning_lines.append(line)
                
                if reasoning_lines:
                    reasoning = "\n".join(reasoning_lines).strip()
                    logger.info(f"Extracted reasoning from answer text (length: {len(reasoning)} chars)")
            
            # Clean up answer text (remove metadata sections)
            clean_answer = answer_text
            if "CITED_CLAIMS:" in clean_answer:
                clean_answer = clean_answer.split("CITED_CLAIMS:")[0].strip()
            if "FIELDS_USED:" in clean_answer:
                clean_answer = clean_answer.split("FIELDS_USED:")[0].strip()
            
            # Extract and format a concise answer - focus on relevant info
            # Try to identify the main answer (usually contains numbers, facts, or direct response)
            lines = [line.strip() for line in clean_answer.split('\n') if line.strip()]
            main_answer = ""
            additional_info = []
            
            # Find the direct answer (usually contains numbers, currency, or key facts)
            for line in lines:
                # Look for lines with numbers, currency, or direct answers
                has_numbers = any(char.isdigit() for char in line)
                has_currency = '$' in line or 'USD' in line.upper()
                has_keywords = any(kw in line.lower() for kw in ['total', 'is', 'are', 'was', 'were', 'equals', 'amount'])
                
                if (has_numbers or has_currency or has_keywords) and not main_answer:
                    # This is likely the main answer
                    main_answer = line
                elif main_answer:
                    # Additional context
                    if len(line) < 150:  # Only include concise additional info
                        additional_info.append(line)
            
            # If we couldn't find a clear main answer, use first meaningful line
            if not main_answer:
                for line in lines:
                    if len(line) > 20:  # Skip very short lines
                        main_answer = line
                        break
                if not main_answer and lines:
                    main_answer = lines[0]
            
            # Limit main answer length (keep it concise - max 150 chars)
            if len(main_answer) > 150:
                # Try to shorten by taking first sentence or truncating
                sentences = main_answer.split('.')
                if len(sentences) > 1:
                    main_answer = sentences[0] + '.'
                else:
                    main_answer = main_answer[:147] + '...'
            
            # Build polished answer: short answer + only relevant additional info
            if additional_info:
                # Only include 1-2 most relevant additional lines (max 100 chars each)
                relevant_info = [info for info in additional_info[:2] if len(info) < 100]
                if relevant_info:
                    polished_answer = f"{main_answer}\n\n" + "\n".join(relevant_info)
                else:
                    polished_answer = main_answer
            else:
                polished_answer = main_answer
            
            logger.info(f"Final polished answer length: {len(polished_answer)} chars")
            
            return {
                "success": True,
                "answer": polished_answer,
                "reasoning": reasoning if reasoning else None,
                "cited_claims": cited_claims,
                "fields_used": fields_used,
                "claims_analyzed": len(claims_context),
                "method": "CAMEL-AI_ChatAgent_OLLAMA_phi3_mini"
            }
        except Exception as e:
            logger.error(f"Error in ChatAgent step: {e}", exc_info=True)
            raise
    
    def _fallback_query(self, query: str, claims_context: List[Dict], scope_description: str) -> Dict[str, Any]:
        """Fallback to local answer generation (no external API)"""
        logger.info("Using local fallback answer generator (no external APIs)")
        
        try:
            from datetime import datetime
            
            # Extract basic stats
            query_lower = query.lower()
            total_claims = len(claims_context)
            total_amount = sum(c.get("total_amount", 0) or 0 for c in claims_context)
            avg_amount = total_amount / total_claims if total_claims > 0 else 0
            
            # Count by status
            status_counts = {}
            for c in claims_context:
                status = c.get("status", "unknown")
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Handle "waiting longest" queries
            if any(word in query_lower for word in ["waiting", "longest", "oldest", "earliest"]):
                waiting_claims = [c for c in claims_context if c.get("status", "") in ['pending_review', 'submitted', 'extracted']]
                if waiting_claims:
                    # Sort by created_at
                    waiting_sorted = sorted(
                        waiting_claims, 
                        key=lambda c: datetime.fromisoformat(c.get("created_at", "2000-01-01").replace('Z', '+00:00')) if c.get("created_at") else datetime.min
                    )
                    longest_waiting = waiting_sorted[0]
                    created_at = longest_waiting.get("created_at", "")
                    if created_at:
                        try:
                            created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            wait_days = (datetime.now() - created_dt.replace(tzinfo=None)).days
                        except:
                            wait_days = 0
                    else:
                        wait_days = 0
                    
                    answer = f"""⏳ Claims Waiting the Longest

The claim that has been waiting the longest:
• Claim Number: {longest_waiting.get('claim_number', 'N/A')}
• Status: {longest_waiting.get('status', 'unknown')}
• Amount: ${longest_waiting.get('total_amount', 0):,.2f}
• Created: {created_at[:10] if created_at else 'Unknown'}
• Waiting: {wait_days} days

Total claims waiting: {len(waiting_claims)} out of {total_claims}"""
                else:
                    answer = f"""⏳ No Claims Currently Waiting

All {total_claims} claims have been processed. No claims are currently pending review."""
            
            # Handle other query types
            elif any(word in query_lower for word in ["total", "sum", "amount"]):
                answer = f"""📊 Claims Financial Summary

Total Claims: {total_claims}
Total Amount: ${total_amount:,.2f}
Average Amount: ${avg_amount:,.2f}"""
            
            elif any(word in query_lower for word in ["pending", "review"]):
                pending = status_counts.get("pending_review", 0) + status_counts.get("submitted", 0) + status_counts.get("extracted", 0)
                pending_amount = sum(c.get("total_amount", 0) or 0 for c in claims_context if c.get("status", "") in ["pending_review", "submitted", "extracted"])
                answer = f"""⏳ Pending Claims Summary

Pending Claims: {pending} out of {total_claims} total
Pending Amount: ${pending_amount:,.2f}"""
            
            elif any(word in query_lower for word in ["approved", "approval"]):
                approved = status_counts.get("approved", 0) + status_counts.get("auto_approved", 0)
                approved_amount = sum(c.get("approved_amount", c.get("total_amount", 0)) or 0 for c in claims_context if c.get("status", "") in ["approved", "auto_approved"])
                approval_rate = (approved / total_claims * 100) if total_claims > 0 else 0
                answer = f"""✅ Approved Claims Summary

Approved Claims: {approved} out of {total_claims}
Approved Amount: ${approved_amount:,.2f}
Approval Rate: {approval_rate:.1f}%"""
            
            else:
                # Default summary
                answer = f"""📋 Claims Summary

Total Claims: {total_claims}
Total Amount: ${total_amount:,.2f}
Average Amount: ${avg_amount:,.2f}

💡 For more specific answers, try asking about:
- Which claims are pending?
- What's the total approved amount?
- Which claims have been waiting the longest?"""
            
            return {
                "success": True,
                "answer": answer,
                "reasoning": "",
                "cited_claims": [],
                "fields_used": ["total_amount", "status", "created_at"],
                "claims_analyzed": len(claims_context),
                "method": "Local_Fallback_Generator"
            }
        except Exception as e:
            logger.error(f"Local fallback query failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "answer": f"I couldn't process that query. Please try a simpler question. (Error: {str(e)[:100]})"
            }
