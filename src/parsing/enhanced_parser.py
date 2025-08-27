# src/parsing/enhanced_parser.py
import re
from typing import Dict, List
from .text_cleaner import clean_skill_list

def enhanced_extract_sections(text: str) -> Dict[str, List[str]]:
    """
    Enhanced section extraction with better pattern matching
    """
    sections = {
        "skills": [],
        "education": [],
        "experience": []
    }
    
    # Common section headers pattern
    section_patterns = {
        "skills": r"(?:skills|technical skills|technologies|expertise)[:\-]?\s*(.*?)(?=education|experience|work|$)",
        "education": r"(?:education|academic background|qualifications)[:\-]?\s*(.*?)(?=experience|skills|work|$)", 
        "experience": r"(?:experience|work history|employment|professional)[:\-]?\s*(.*?)(?=education|skills|$)"
    }
    
    text_lower = text.lower()
    
    for section, pattern in section_patterns.items():
        match = re.search(pattern, text_lower, re.IGNORECASE | re.DOTALL)
        if match:
            content = match.group(1).strip()
            
            # Split into list items with better handling
            if section == "skills":
                # Special handling for skills section
                items = split_skills_string(content)
            else:
                # Regular splitting for other sections
                items = [item.strip() for item in re.split(r'[\n•\-]', content) if item.strip()]
            
            sections[section] = items
    
    # Clean skills specifically
    if sections["skills"]:
        sections["skills"] = clean_skill_list(sections["skills"])
    
    return sections

def split_skills_string(skills_text: str) -> List[str]:
    """
    Split a string of skills into individual skills with smart parsing
    """
    if not skills_text:
        return []
    
    skills = []
    
    # First try splitting by common delimiters
    if any(delimiter in skills_text for delimiter in [',', ';', '•', '\n', '/']):
        skills = [skill.strip() for skill in re.split(r'[,;•\n/]', skills_text) if skill.strip()]
    else:
        # If no delimiters, try to split by common patterns
        # Handle "Python Machine Learning SQL" pattern
        skills = re.split(r'\s{2,}', skills_text)  # Split on multiple spaces
        skills = [skill.strip() for skill in skills if skill.strip()]
        
        # If still not split properly, try uppercase splitting
        if len(skills) <= 1:
            skills = split_skills_by_uppercase(skills_text)
    
    return skills

def split_skills_by_uppercase(text: str) -> List[str]:
    """
    Split a string of skills by uppercase letters
    Example: "PythonMachineLearningSQL" -> ["Python", "Machine", "Learning", "SQL"]
    """
    # Split on uppercase letters (camelCase)
    skills = re.findall(r'[A-Z][a-z]+|[A-Z]+(?=[A-Z]|$)', text)
    return [skill.strip() for skill in skills if skill.strip()]