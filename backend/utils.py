"""
Utility functions for the expense management system
"""
from datetime import datetime
from typing import Optional
import re


def parse_date(date_string: str) -> Optional[datetime]:
    """
    Parse various date formats from receipts
    
    Args:
        date_string: Date string in various formats
        
    Returns:
        Parsed datetime object or None
    """
    if not date_string:
        return None
    
    # Common date formats
    date_formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%Y-%m-%d %H:%M:%S",
        "%m-%d-%Y",
        "%d-%m-%Y",
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_string.strip(), fmt)
        except ValueError:
            continue
    
    return None


def extract_amount(text: str) -> Optional[float]:
    """
    Extract monetary amount from text
    
    Args:
        text: Text containing amount
        
    Returns:
        Extracted amount as float or None
    """
    if not text:
        return None
    
    # Remove currency symbols and extract numbers
    # Pattern: $123.45, 123.45, €123,45, etc.
    patterns = [
        r'\$?\s*(\d+[.,]\d{2})',  # $123.45 or 123.45
        r'(\d+[.,]\d{2})',        # 123.45
        r'(\d+)',                 # 123
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.replace(',', ''))
        if match:
            try:
                amount = float(match.group(1).replace(',', '.'))
                return amount
            except ValueError:
                continue
    
    return None


def normalize_merchant_name(name: str) -> str:
    """
    Normalize merchant name for better duplicate detection
    
    Args:
        name: Merchant name
        
    Returns:
        Normalized merchant name
    """
    if not name:
        return ""
    
    # Convert to lowercase
    normalized = name.lower().strip()
    
    # Remove common suffixes
    suffixes = ['inc', 'llc', 'ltd', 'corp', 'co', 'company']
    for suffix in suffixes:
        if normalized.endswith(f' {suffix}') or normalized.endswith(f'.{suffix}'):
            normalized = normalized[:-len(suffix)-1].strip()
    
    # Remove special characters (keep spaces and alphanumeric)
    normalized = re.sub(r'[^\w\s]', '', normalized)
    
    # Remove extra spaces
    normalized = ' '.join(normalized.split())
    
    return normalized


def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format amount as currency string
    
    Args:
        amount: Amount to format
        currency: Currency code
        
    Returns:
        Formatted currency string
    """
    currency_symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "CNY": "¥",
        "JPY": "¥",
    }
    
    symbol = currency_symbols.get(currency, currency)
    
    if currency == "JPY":
        return f"{symbol}{amount:.0f}"
    else:
        return f"{symbol}{amount:.2f}"

