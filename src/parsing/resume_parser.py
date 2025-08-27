# src/parsing/resume_parser.py
import re
from typing import Dict, List, Optional

def extract_sections(text: str) -> Dict[str, List[str]]:
    """
    Extract structured fields from resume text with flexible matching.
    Handles variations like: skills, technical skills, technologies, etc.
    """
    sections = {
        "skills": [],
        "education": [], 
        "experience": []
    }

    text_lower = text.lower()
    
    # --- Enhanced Skills Extraction ---
    skills_patterns = [
        r"(technical\s+skills|skills|technologies|expertise|competencies)[:\-]?\s*(.*?)(?=education|experience|work|$)",
        r"(programming\s+languages|tools|software\s+skills)[:\-]?\s*(.*?)(?=education|experience|work|$)",
    ]
    
    for pattern in skills_patterns:
        skills_match = re.search(pattern, text_lower, re.IGNORECASE | re.DOTALL)
        if skills_match:
            skills_text = skills_match.group(2).strip()
            
            # IMPROVED: Better skill splitting that handles spaces
            # Split by commas, semicolons, bullets, newlines, OR multiple consecutive skills
            skills = []
            
            # First try splitting by common delimiters
            if any(delimiter in skills_text for delimiter in [',', ';', '•', '\n']):
                skills = [skill.strip() for skill in re.split(r'[,;•\n]', skills_text) if skill.strip()]
            else:
                # If no delimiters, try to split by common skill patterns
                # This handles "Python Machine Learning SQL" -> ["Python", "Machine Learning", "SQL"]
                skills = split_skills_by_uppercase(skills_text)
            
            sections["skills"].extend(skills)
            break  # Stop after first match

    # --- Keep the rest of your function the same ---
    # --- Enhanced Education Extraction ---
    education_patterns = [
        r"(education|academic\s+background|qualifications|degrees)[:\-]?\s*(.*?)(?=experience|skills|work|$)",
        r"(university|college|school|bachelor|master|phd)[\s\w]*[:\-]?\s*(.*?)(?=experience|skills|work|$)",
    ]
    
    for pattern in education_patterns:
        edu_match = re.search(pattern, text_lower, re.IGNORECASE | re.DOTALL)
        if edu_match:
            edu_text = edu_match.group(2).strip() if edu_match.group(2) else edu_match.group(1)
            education = [edu.strip() for edu in re.split(r'[\n•]', edu_text) if edu.strip()]
            sections["education"].extend(education)
            break

    # --- Enhanced Experience Extraction ---
    experience_patterns = [
        r"(experience|work\s+history|employment|professional)[:\-]?\s*(.*?)(?=education|skills|$)",
        r"(internship|work|job|position)[\s\w]*[:\-]?\s*(.*?)(?=education|skills|$)",
    ]
    
    for pattern in experience_patterns:
        exp_match = re.search(pattern, text_lower, re.IGNORECASE | re.DOTALL)
        if exp_match:
            exp_text = exp_match.group(2).strip() if exp_match.group(2) else edu_match.group(1)
            experience = [exp.strip() for exp in re.split(r'[\n•]', exp_text) if exp.strip()]
            sections["experience"].extend(experience)
            break

    # Remove duplicates and empty entries
    for key in sections:
        sections[key] = list(set([item for item in sections[key] if item]))
    
    return sections

def split_skills_by_uppercase(text: str) -> List[str]:
    """
    Split a string of skills by uppercase letters (camelCase splitting)
    Example: "PythonMachineLearningSQL" -> ["Python", "Machine", "Learning", "SQL"]
    """
    # Split on uppercase letters followed by lowercase (camelCase)
    skills = re.findall(r'[A-Z][a-z]+|[A-Z]+(?=[A-Z]|$)', text)
    return [skill.strip() for skill in skills if skill.strip()]