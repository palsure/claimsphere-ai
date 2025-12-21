"""
ERNIE API integration for expense understanding and categorization
"""
import os
import json
import requests
from typing import Dict, List, Optional
from datetime import datetime
import hashlib
import time


class ErnieService:
    """Service for interacting with Baidu AI Studio ERNIE API"""
    
    def __init__(self, api_key: Optional[str] = None, secret_key: Optional[str] = None):
        """
        Initialize ERNIE service
        
        Args:
            api_key: Baidu AI Studio API key
            secret_key: Baidu AI Studio secret key
        """
        self.api_key = api_key or os.getenv('BAIDU_API_KEY', '')
        self.secret_key = secret_key or os.getenv('BAIDU_SECRET_KEY', '')
        self.access_token = None
        self.token_expires_at = 0
        self.base_url = "https://aip.baidubce.com"
    
    def get_access_token(self) -> str:
        """
        Get access token for Baidu API (cached for 30 days)
        
        Returns:
            Access token string
        """
        # Check if token is still valid (with 1 hour buffer)
        if self.access_token and time.time() < self.token_expires_at - 3600:
            return self.access_token
        
        url = f"{self.base_url}/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }
        
        try:
            response = requests.post(url, params=params)
            response.raise_for_status()
            data = response.json()
            self.access_token = data.get("access_token")
            # Tokens typically expire in 30 days, but we'll refresh after 29 days
            self.token_expires_at = time.time() + (29 * 24 * 3600)
            return self.access_token
        except Exception as e:
            print(f"Error getting access token: {e}")
            # Fallback: return a mock token for development
            if not self.api_key:
                return "mock_token_for_development"
            raise
    
    def call_ernie_api(self, messages: List[Dict], model: str = "ernie-4.0-8k") -> Dict:
        """
        Call ERNIE chat completion API
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model name (ernie-4.0-8k, ernie-3.5-8k, etc.)
            
        Returns:
            API response dictionary
        """
        token = self.get_access_token()
        url = f"{self.base_url}/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/{model}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        params = {
            "access_token": token
        }
        
        payload = {
            "messages": messages,
            "temperature": 0.7,
            "top_p": 0.8
        }
        
        try:
            response = requests.post(url, headers=headers, params=params, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error calling ERNIE API: {e}")
            # Fallback for development without API key
            if not self.api_key:
                return {
                    "result": "Mock response: This is a development mode response. Please configure your Baidu API credentials.",
                    "usage": {"total_tokens": 100}
                }
            raise
    
    def extract_claim_info(self, ocr_text: str, layout_info: Optional[List] = None) -> Dict:
        """
        Extract structured claim information from OCR text using ERNIE
        
        Args:
            ocr_text: Text extracted from claim document
            layout_info: Optional layout information from OCR
            
        Returns:
            Dictionary with extracted claim information
        """
        prompt = f"""You are an expert at extracting information from insurance claims, medical claims, and claim forms. 
Extract the following information from this claim document text and return it as a JSON object:

{ocr_text}

Extract and return a JSON object with these fields:
- claimant_name: The name of the person or entity filing the claim
- date_of_incident: The date when the incident occurred (ISO format: YYYY-MM-DD)
- total_amount: The total claim amount (number only, no currency symbol)
- currency: The currency code (USD, CNY, EUR, etc.)
- claim_type: One of: medical, insurance, travel, property, business, other
- policy_number: The policy or reference number if visible
- description: A description of the claim/incident
- items: Array of claim items, each with description, quantity, unit_price, and amount
- notes: Any additional relevant information

Return ONLY valid JSON, no other text."""

        messages = [
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.call_ernie_api(messages)
            result_text = response.get("result", "")
            
            # Try to parse JSON from response
            # ERNIE might wrap JSON in markdown code blocks
            if "```json" in result_text:
                json_start = result_text.find("```json") + 7
                json_end = result_text.find("```", json_start)
                result_text = result_text[json_start:json_end].strip()
            elif "```" in result_text:
                json_start = result_text.find("```") + 3
                json_end = result_text.find("```", json_start)
                result_text = result_text[json_start:json_end].strip()
            
            claim_data = json.loads(result_text)
            return claim_data
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from ERNIE response: {e}")
            print(f"Response was: {result_text}")
            # Return a fallback structure
            return {
                "claimant_name": "Unknown",
                "date_of_incident": datetime.now().isoformat()[:10],
                "total_amount": 0.0,
                "currency": "USD",
                "claim_type": "other",
                "items": [],
                "description": "Failed to parse claim information"
            }
        except Exception as e:
            print(f"Error extracting claim info: {e}")
            # Fallback: try to extract basic info from OCR text directly
            return self._extract_basic_info_from_text(ocr_text)
    
    def _extract_basic_info_from_text(self, ocr_text: str) -> Dict:
        """
        Fallback method to extract basic claim info directly from OCR text
        when ERNIE API is unavailable.
        """
        import re
        
        result = {
            "claimant_name": "Unknown",
            "date_of_incident": datetime.now().isoformat()[:10],
            "total_amount": 0.0,
            "currency": "USD",
            "claim_type": "other",
            "items": [],
            "description": ocr_text[:200] if ocr_text else "No description"
        }
        
        # Extract amounts (look for currency patterns)
        amount_patterns = [
            r'\$\s*([\d,]+\.?\d*)',  # $50.00 or $1,500.00
            r'(?:total|amount|sum|price|cost|charge)[\s:]*\$?\s*([\d,]+\.?\d*)',  # Total: 50.00
            r'([\d,]+\.?\d*)\s*(?:dollars|usd|USD)',  # 50.00 dollars
            r'¥\s*([\d,]+\.?\d*)',  # Chinese Yuan
            r'€\s*([\d,]+\.?\d*)',  # Euro
            r'£\s*([\d,]+\.?\d*)',  # British Pound
        ]
        
        amounts = []
        for pattern in amount_patterns:
            matches = re.findall(pattern, ocr_text, re.IGNORECASE)
            for match in matches:
                try:
                    amount = float(match.replace(',', ''))
                    if amount > 0:
                        amounts.append(amount)
                except ValueError:
                    continue
        
        # Use the largest amount found (likely the total)
        if amounts:
            result["total_amount"] = max(amounts)
        
        # Extract dates
        date_patterns = [
            r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})',  # 2024-01-15
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})',  # 01/15/2024
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{2})',  # 01/15/24
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, ocr_text)
            if match:
                date_str = match.group(1)
                # Try to parse the date
                for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y', '%m-%d-%Y', '%m/%d/%y', '%m-%d-%y']:
                    try:
                        parsed_date = datetime.strptime(date_str, fmt)
                        result["date_of_incident"] = parsed_date.isoformat()[:10]
                        break
                    except ValueError:
                        continue
                break
        
        # Detect currency
        if '¥' in ocr_text or 'CNY' in ocr_text.upper():
            result["currency"] = "CNY"
        elif '€' in ocr_text or 'EUR' in ocr_text.upper():
            result["currency"] = "EUR"
        elif '£' in ocr_text or 'GBP' in ocr_text.upper():
            result["currency"] = "GBP"
        
        # Try to detect claim type from keywords
        text_lower = ocr_text.lower()
        if any(kw in text_lower for kw in ['medical', 'hospital', 'doctor', 'pharmacy', 'prescription', 'health']):
            result["claim_type"] = "medical"
        elif any(kw in text_lower for kw in ['insurance', 'policy', 'coverage', 'premium']):
            result["claim_type"] = "insurance"
        elif any(kw in text_lower for kw in ['travel', 'flight', 'hotel', 'airline', 'booking']):
            result["claim_type"] = "travel"
        elif any(kw in text_lower for kw in ['property', 'damage', 'home', 'house', 'repair']):
            result["claim_type"] = "property"
        elif any(kw in text_lower for kw in ['business', 'expense', 'office', 'supplies', 'equipment']):
            result["claim_type"] = "business"
        
        # Try to extract claimant name (look for "Name:" or similar patterns)
        name_patterns = [
            r'(?:name|claimant|patient|customer)[\s:]+([A-Za-z\s]+?)(?:\n|$|,)',
            r'^([A-Z][a-z]+\s+[A-Z][a-z]+)',  # First line with proper name format
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, ocr_text, re.IGNORECASE | re.MULTILINE)
            if match:
                name = match.group(1).strip()
                if len(name) > 2 and len(name) < 50:
                    result["claimant_name"] = name
                    break
        
        return result

    def categorize_claim(self, claimant_name: str, description: str, amount: float) -> str:
        """
        Categorize a claim based on description and context
        
        Args:
            claimant_name: Name of the claimant
            description: Claim description
            amount: Total amount
            
        Returns:
            Claim type string
        """
        prompt = f"""Categorize this claim into one of these types:
medical, insurance, travel, property, business, other

Claimant: {claimant_name}
Description: {description}
Amount: ${amount}

Return ONLY the claim type, nothing else."""

        messages = [
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.call_ernie_api(messages)
            category = response.get("result", "other").strip().lower()
            
            # Validate category
            valid_categories = [
                "meals", "travel", "office_supplies", "utilities",
                "software", "marketing", "professional_services",
                "rent", "insurance", "other"
            ]
            
            if category in valid_categories:
                return category
            else:
                return "other"
        except Exception as e:
            print(f"Error categorizing expense: {e}")
            return "other"
    
    def answer_claim_query(self, query: str, claims_context: List[Dict]) -> str:
        """
        Answer natural language questions about claims
        
        Args:
            query: Natural language question
            claims_context: List of claim dictionaries for context
            
        Returns:
            Answer string
        """
        # Summarize claims for context (limit to recent ones)
        context_summary = json.dumps(claims_context[-20:], indent=2, default=str)
        
        prompt = f"""You are a claim processing assistant. Answer the user's question about insurance/medical claims.

Claim Data:
{context_summary}

User Question: {query}

Provide a clear, helpful answer based on the claim data. If the question requires calculations, show your work."""

        messages = [
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.call_ernie_api(messages)
            return response.get("result", "I couldn't process that query.")
        except Exception as e:
            print(f"Error answering query: {e}")
            # Fallback: provide basic analytics from the data
            return self._fallback_query_answer(query, claims_context)
    
    def _fallback_query_answer(self, query: str, claims: List[Dict]) -> str:
        """Provide basic answers when ERNIE API is unavailable"""
        query_lower = query.lower()
        
        if not claims:
            return "No claims found in the system. Please upload some claim documents first."
        
        # Calculate basic statistics
        total_claims = len(claims)
        total_amount = sum(c.get('total_amount', 0) for c in claims)
        
        # Count by status
        status_counts = {}
        for c in claims:
            status = c.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Count by type
        type_counts = {}
        type_amounts = {}
        for c in claims:
            claim_type = c.get('claim_type', 'other')
            type_counts[claim_type] = type_counts.get(claim_type, 0) + 1
            type_amounts[claim_type] = type_amounts.get(claim_type, 0) + c.get('total_amount', 0)
        
        pending_count = status_counts.get('pending', 0)
        pending_amount = sum(c.get('total_amount', 0) for c in claims if c.get('status') == 'pending')
        approved_count = status_counts.get('approved', 0)
        
        # Match query patterns
        if 'total' in query_lower and ('amount' in query_lower or 'pending' in query_lower):
            return f"Total pending claims: {pending_count} claims worth ${pending_amount:,.2f}"
        
        if 'medical' in query_lower:
            medical_count = type_counts.get('medical', 0)
            medical_amount = type_amounts.get('medical', 0)
            return f"Medical claims: {medical_count} claims totaling ${medical_amount:,.2f}"
        
        if 'average' in query_lower and 'time' in query_lower:
            return "Average processing time tracking requires completed claims with timestamps. Currently processing claims in real-time."
        
        if 'highest' in query_lower or 'most' in query_lower:
            if type_amounts:
                highest_type = max(type_amounts.items(), key=lambda x: x[1])
                return f"The claim type with highest amount is '{highest_type[0]}' with ${highest_type[1]:,.2f}"
        
        # Default summary
        return f"""Claims Summary:
• Total claims: {total_claims}
• Total amount: ${total_amount:,.2f}
• Pending: {pending_count} (${pending_amount:,.2f})
• Approved: {approved_count}
• Claim types: {', '.join(f'{k}: {v}' for k, v in type_counts.items())}

Note: AI-powered detailed analysis is temporarily unavailable. Please check your Baidu API credentials."""
    
    def generate_claim_summary(self, claims: List[Dict]) -> str:
        """
        Generate a natural language summary of claims
        
        Args:
            claims: List of claim dictionaries
            
        Returns:
            Summary text
        """
        claims_json = json.dumps(claims, indent=2, default=str)
        
        prompt = f"""Generate a concise summary of these claims in natural language:

{claims_json}

Include:
- Total claims and amounts
- Status breakdown
- Claim types
- Notable trends
- Any recommendations

Keep it under 200 words."""

        messages = [
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.call_ernie_api(messages)
            return response.get("result", "Unable to generate summary.")
        except Exception as e:
            print(f"Error generating summary: {e}")
            return f"Error: {str(e)}"
    
    def validate_claim_with_ai(self, claim_data: Dict) -> Dict:
        """
        Use ERNIE to validate claim data and provide recommendations
        
        Args:
            claim_data: Claim data dictionary
            
        Returns:
            Dictionary with validation results and recommendations
        """
        claim_json = json.dumps(claim_data, indent=2, default=str)
        
        prompt = f"""You are a claim validation expert. Review this claim data and provide validation feedback:

{claim_json}

Return a JSON object with:
- is_valid: boolean
- validation_errors: array of error messages
- recommendations: array of recommendations
- risk_level: "low", "medium", or "high"
- requires_manual_review: boolean

Return ONLY valid JSON, no other text."""

        messages = [
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.call_ernie_api(messages)
            result_text = response.get("result", "")
            
            # Try to parse JSON
            if "```json" in result_text:
                json_start = result_text.find("```json") + 7
                json_end = result_text.find("```", json_start)
                result_text = result_text[json_start:json_end].strip()
            elif "```" in result_text:
                json_start = result_text.find("```") + 3
                json_end = result_text.find("```", json_start)
                result_text = result_text[json_start:json_end].strip()
            
            validation_result = json.loads(result_text)
            return validation_result
        except Exception as e:
            print(f"Error validating claim with AI: {e}")
            return {
                "is_valid": True,
                "validation_errors": [],
                "recommendations": ["Unable to perform AI validation"],
                "risk_level": "medium",
                "requires_manual_review": True
            }
