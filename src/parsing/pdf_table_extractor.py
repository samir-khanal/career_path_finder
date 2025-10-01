import pdfplumber
import re
from typing import List

def extract_skills_from_pdf_tables(pdf_path: str) -> List[str]:
    """
    Extract skills from PDF tables using pdfplumber
    """
    skills = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                # Extract tables
                tables = page.extract_tables()
                
                for table in tables:
                    if not table:
                        continue
                    
                    # Check if this looks like a skills table
                    if is_skills_table(table):
                        # Extract skills from table cells
                        for row in table:
                            for cell in row:
                                if cell and isinstance(cell, str):
                                    cell_text = cell.strip()
                                    if cell_text and looks_like_skill(cell_text):
                                        skills.append(cell_text)
                                
    except Exception as e:
        print(f"PDF table extraction error: {e}")
    
    return skills

def is_skills_table(table_data: List[List[str]]) -> bool:
    """
    Check if a table is likely to contain skills
    """
    if not table_data or len(table_data) < 1:
        return False
    
    # Check header row for skill-related keywords
    header_text = ' '.join([str(cell or '') for cell in table_data[0]]).lower()
    
    skill_keywords = {'skill', 'technology', 'tool', 'language', 'framework', 
                     'proficiency', 'expertise', 'competency', 'technical'}
    
    return any(keyword in header_text for keyword in skill_keywords)

def looks_like_skill(text: str) -> bool:
    """
    Simple heuristic to identify skill-like text
    """
    # Skip table headers and metadata
    if any(keyword in text.lower() for keyword in ['years', 'proficiency', 'level', 
                                                  'rating', 'skill', 'technology', 
                                                  'category', 'tool']):
        return False
    
    # Skip numbers and very short text
    if text.isdigit() or len(text) < 2:
        return False
        
    # Skip very long text (probably descriptions)
    if len(text) > 30:
        return False
        
    # skills contain letters and reasonable characters
    if re.match(r'^[A-Za-z0-9\s\+\.\/#-]{2,30}$', text):
        return True
        
    return False