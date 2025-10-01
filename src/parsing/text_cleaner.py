# src/parsing/text_cleaner.py
import re
from typing import List, Optional

def clean_extracted_text(text: str) -> Optional[str]:
    """Clean and normalize extracted text"""
    if not text or not isinstance(text, str):
        return None
        
    # Basic cleaning
    text = re.sub(r'\s+', ' ', text)  # Replace all whitespace with single spaces
    text = text.strip()
    
    # Remove common artifacts
    text = re.sub(r'(?i)\b(page|confidential)\b.*?\d+', '', text)  # Page numbers
    text = re.sub(r'\x0c', ' ', text)  # Form feeds   
     
    return text if text else None

def clean_skill_list(skills: List[str]) -> List[str]:
    """Clean and normalize a list of skills - FIXED VERSION"""
    cleaned = []
    seen = set()

    skill_normalizations = {
        'objective-c': 'objective-c',
        'objective c': 'objective-c', 
        'cocoa touch': 'cocoa touch',
        'cocoa': 'cocoa touch',
        'nsuserdefaults': 'nsuserdefaults',
        'node.js': 'node',
        'node': 'node',
        'rest': 'rest',
        'soap': 'soap',
        'xml': 'xml', 
        'json': 'json',
        'sqlite': 'sqlite',
        'plist': 'plist',
    }
    
    for skill in skills:
        if not skill or not isinstance(skill, str):
            continue
            
        # Clean the skill
        skill_clean = skill.strip()
        skill_clean = re.sub(r'[^\w\s]', '', skill_clean)  # Remove special chars
        skill_clean = re.sub(r'\s+', ' ', skill_clean)  # Normalize spaces
        
        if not skill_clean or len(skill_clean) < 2:
            continue
            
        # ✅ CRITICAL FIX: Don't use .title() - it ruins acronyms like SQL -> Sql
        # Instead, keep original case but normalize for comparison
        skill_lower = skill_clean.lower()
        skill_normalized = skill_normalizations.get(skill_lower, skill_lower)
        
        # Avoid duplicates using normalized form
        if skill_normalized not in seen:
            seen.add(skill_normalized)
            cleaned.append(skill_clean)  # Keep original capitalization
    
    return cleaned