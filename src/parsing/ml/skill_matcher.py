# src/ml/skill_matcher.py
from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import re

# Fix import paths - remove the problematic import
try:
    from src.parsing import parse_resume
except ImportError:
    # Fallback for direct execution
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from src.parsing import parse_resume

# ----------------------------
# Paths - FIXED
# ----------------------------
PROJ_ROOT = Path(__file__).resolve().parents[2]  # Changed from 3 to 2
MODELS_DIR = PROJ_ROOT / "models"
DATASET_CSV = MODELS_DIR / "skills_dataset.csv"
MODEL_PATH = MODELS_DIR / "trained_model.pkl"
VECT_PATH = MODELS_DIR / "vectorizer.pkl"

# ----------------------------
# Skill Synonyms Mapping (Keep your existing)
# ----------------------------
SKILL_SYNONYMS = {
    "python": ["python", "py", "python3", "python programming"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "data visualization": ["data visualization", "visualization", "matplotlib", "seaborn"],
    "sql": ["sql", "mysql", "postgresql"],
    "statistics": ["statistics", "stats"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "eda": ["eda", "exploratory data analysis"],
    "communication": ["communication", "communication skills"],
    "swift": ["swift", "swift programming"],
    "ios": ["ios", "apple ios"],
    "rest": ["rest", "rest api", "restful", "restful api"],
    "soap": ["soap", "soap api"],
    "mvc": ["mvc", "model view controller"],
    "api": ["api", "apis", "web services"],
    "networking": ["networking", "ccna", "routing", "switching"],
    "cloud": ["cloud", "aws", "azure", "gcp"],
    # ... keep the rest of your SKILL_SYNONYMS
}

def normalize_skill_to_base(skill: str) -> str:
    """Normalize skill to base form"""
    if not skill:
        return ""
    
    skill_lower = skill.lower().strip()
    skill_lower = re.sub(r'[^\w\s]', '', skill_lower)
    skill_lower = re.sub(r'\s+', ' ', skill_lower)
    
    for base_skill, synonyms in SKILL_SYNONYMS.items():
        if skill_lower in synonyms or skill_lower == base_skill:
            return base_skill
    
    return skill_lower

def debug_skill_matching(resume_skills: List[str], required_skills: List[str]):
    """Debug function to see skill matching process"""
    print("=== DEBUG SKILL MATCHING ===")
    print(f"Original resume skills: {resume_skills}")
    print(f"Original required skills: {required_skills}")
    
    normalized_resume = [normalize_skill_to_base(s) for s in resume_skills]
    normalized_required = [normalize_skill_to_base(s) for s in required_skills]
    
    print(f"Normalized resume: {normalized_resume}")
    print(f"Normalized required: {normalized_required}")
    
    matched = set(normalized_resume) & set(normalized_required)
    missing = set(normalized_required) - set(normalized_resume)
    
    print(f"Matched: {matched}")
    print(f"Missing: {missing}")
    print("========================")

# ----------------------------
# Data loaders - SIMPLIFIED
# ----------------------------
def load_skill_dataset() -> Dict[str, List[str]]:
    """
    Load job roles with REALISTIC skill overlaps
    """
    print("🔄 Loading realistic skill dataset with overlaps...")
    
    return {
        'Junior Data Scientist': [
            'python', 'pandas', 'sql', 'statistics', 'machine learning', 
            'data visualization', 'scikit-learn', 'numpy', 'git'
        ],
        'Senior Data Scientist': [
            'python', 'machine learning', 'deep learning', 'sql', 'aws',
            'statistics', 'tensorflow', 'pytorch', 'spark', 'big data',
            'docker', 'kubernetes', 'mlops', 'nlp'
        ],
        'ML Engineer': [
            'python', 'machine learning', 'tensorflow', 'pytorch', 'docker',
            'aws', 'deep learning', 'kubernetes', 'mlops', 'computer vision',
            'nlp', 'git'
        ],
        'Data Analyst': [
            'sql', 'python', 'excel', 'tableau', 'power bi', 'statistics',
            'data visualization', 'pandas', 'data analysis', 'reporting'
        ],
        'Data Engineer': [
            'python', 'sql', 'aws', 'spark', 'docker', 'kubernetes',
            'etl', 'big data', 'airflow', 'kafka'
        ],
        'Business Analyst': [
            'sql', 'excel', 'tableau', 'power bi', 'requirements', 'documentation',
            'communication', 'project management'
        ]
    }

def parse_resume_structured(file_path: str) -> Dict[str, List[str]]:
    """Parse resume and return structured data - FIXED VERSION"""
    try:
        result = parse_resume(file_path)
        
        if result and isinstance(result, dict):
            skills = result.get("skills", [])
            # Ensure skills is always a list
            if isinstance(skills, str):
                skills = [skills]
            
            return {
                "skills": skills,
                "education": result.get("education", []),
                "experience": result.get("experience", [])
            }
        
        return {"skills": [], "education": [], "experience": []}
        
    except Exception as e:
        print(f"Error in parse_resume_structured: {e}")
        return {"skills": [], "education": [], "experience": []}

def compute_skill_gap(resume_skills: List[str], required_skills: List[str]) -> Dict[str, List[str]]:
    """Compute skill gap with proper normalization"""
    normalized_resume = set()
    for skill in resume_skills:
        normalized = normalize_skill_to_base(skill)
        if normalized:
            normalized_resume.add(normalized)
    
    skill_mapping = {}
    normalized_required = set()
    
    for skill in required_skills:
        normalized = normalize_skill_to_base(skill)
        if normalized:
            normalized_required.add(normalized)
            skill_mapping[normalized] = skill
    
    matched_normalized = normalized_resume & normalized_required
    missing_normalized = normalized_required - normalized_resume
    
    matched = [skill_mapping[skill] for skill in matched_normalized]
    missing = [skill_mapping[skill] for skill in missing_normalized]
    
    return {"matched": matched, "missing": missing}

def analyze_resume(file_path: str, chosen_role: Optional[str] = None) -> Dict:
    """End-to-end resume analysis with debug info - FIXED VERSION"""
    roles_map = load_skill_dataset()
    structured = parse_resume_structured(file_path)

    # DEBUG: Show what was parsed
    print(f"DEBUG: Parsed skills: {structured.get('skills', [])}")
    print(f"DEBUG: Skills type: {type(structured.get('skills', []))}")
    print(f"DEBUG: Skills count: {len(structured.get('skills', []))}")
    
    skills_list = structured.get("skills", [])
    
    # Simple role prediction based on skill matching
    predictions = []
    for role, required_skills in roles_map.items():
        gap_result = compute_skill_gap(skills_list, required_skills)
        match_score = (len(gap_result["matched"]) / len(required_skills)) * 100 if required_skills else 0
        predictions.append((role, match_score))
    
    # Sort by score
    predictions.sort(key=lambda x: x[1], reverse=True)
    
    if chosen_role is None:
        chosen_role = predictions[0][0] if predictions else next(iter(roles_map.keys()))

    required = roles_map.get(chosen_role, [])
    
    # DEBUG: Show matching process
    print(f"DEBUG: Required skills for {chosen_role}: {required}")
    debug_skill_matching(skills_list, required)
    
    gap = compute_skill_gap(skills_list, required)

    total = len(required)
    score = (len(gap["matched"]) / total) * 100 if total > 0 else 0.0

    return {
        "parsed": structured,
        "predictions": predictions[:3],  # Top 3
        "chosen_role": chosen_role,
        "required_skills": required,
        "gap": gap,
        "match_score": score
    }