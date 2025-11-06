# src/parsing/text_cleaner.py
import re
from typing import List, Optional

def clean_extracted_text(text: str) -> Optional[str]:
    """Clean and normalize extracted text WHILE PRESERVING STRUCTURE"""
    if not text or not isinstance(text, str):
        return None
        
    # PRESERVE structure - only clean, don't destroy formatting
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Clean individual lines but preserve their structure
        line = re.sub(r'\s+', ' ', line)  # Clean spaces WITHIN lines only
        line = re.sub(r'(?i)\b(page|confidential)\b.*?\d+', '', line)  # Remove page numbers
        line = re.sub(r'\x0c', ' ', line)  # Form feeds
        
        if line.strip():  # Only add non-empty lines
            cleaned_lines.append(line.strip())
    
    # Join back with newlines to preserve section boundaries
    text = '\n'.join(cleaned_lines)
    
    return text if text else None

def clean_and_preserve_structure(text: str) -> str:
    """
    Enhanced cleaning that specifically preserves resume structure
    """
    if not text:
        return ""
    
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Detect section headers (ALL CAPS or Title Case with reasonable length)
        is_section_header = (
            (line.isupper() and 3 < len(line) < 100) or
            (line.istitle() and len(line) < 80) or
            any(header in line.lower() for header in [
                'education', 'experience', 'skills', 'projects', 
                'certifications', 'summary', 'work history'
            ])
        )
        
        # Add extra spacing around section headers for better parsing
        if is_section_header and cleaned_lines:
            cleaned_lines.append('')  # Blank line before section
            cleaned_lines.append(line)
            cleaned_lines.append('')  # Blank line after section header
        else:
            cleaned_lines.append(line)
    
    cleaned_text = '\n'.join(cleaned_lines)
    
    # Fix common extraction artifacts
    replacements = {
        '|': 'I',      # Common OCR error
        '—': '-',      # Replace em dash
        '�': '',       # Remove replacement chars
        '\x0c': '\n',  # Form feed to newline
    }
    
    for old, new in replacements.items():
        cleaned_text = cleaned_text.replace(old, new)
    
    return cleaned_text

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