import re
from typing import Optional

def clean_extracted_text(text: str) -> Optional[str]:
    """
    Normalize extracted text from any format
    
    Args:
        text: Raw extracted text
        
    Returns:
        Cleaned text with:
        - Normalized whitespace
        - Removed page numbers/headers
        - Standardized encodings
    """
    if not text or not isinstance(text, str):
        return None
        
    # 1. Basic cleaning
    text = re.sub(r'\s+', ' ', text)  # Replace all whitespace with single spaces
    text = text.strip()
    
    # 2. Remove common artifacts
    text = re.sub(r'(?i)\b(page|confidential)\b.*?\d+', '', text)  # Page numbers
    text = re.sub(r'\x0c', ' ', text)  # Form feeds
    
    # 3. Normalize skill representations
    replacements = {
        r'\bjs\b': 'JavaScript',
        r'\breactjs\b': 'React'
    }
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text if text else None