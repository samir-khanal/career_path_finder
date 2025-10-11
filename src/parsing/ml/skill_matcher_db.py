from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import re

try:
    from src.parsing import parse_resume
    from src.database import SkillRepository
except ImportError:
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from src.parsing import parse_resume
    from src.database import SkillRepository

PROJ_ROOT = Path(__file__).resolve().parents[3]

SKILL_SYNONYMS = {
    "python": ["python", "py", "python3", "python programming"],
    "javascript": ["javascript", "js", "ecmascript", "es6", "es2015"],
    "java": ["java", "java programming"],
    "pandas": ["pandas", "pd"],
    "numpy": ["numpy", "np"],
    "react": ["react", "reactjs", "react.js"],
    "node.js": ["node", "nodejs", "node.js"],
    "sql": ["sql", "mysql", "postgresql", "postgres", "structured query language"],
    "machine learning": ["machine learning", "ml", "statistical learning"],
    "deep learning": ["deep learning", "dl", "neural networks"],
    "data visualization": ["data visualization", "visualization", "matplotlib", "seaborn", "plotly"],
    "statistics": ["statistics", "stats", "statistical analysis"],
    "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
    "tensorflow": ["tensorflow", "tf"],
    "pytorch": ["pytorch", "torch"],
    "docker": ["docker", "containerization"],
    "kubernetes": ["kubernetes", "k8s"],
    "aws": ["aws", "amazon web services", "amazon aws"],
    "azure": ["azure", "microsoft azure"],
    "git": ["git", "github", "gitlab", "version control"],
    "rest api": ["rest", "rest api", "restful", "api"],
    "agile": ["agile", "scrum", "agile methodology"],
    "communication": ["communication", "communication skills", "verbal communication"],
}

def build_skill_synonyms_from_db(skill_repo: SkillRepository) -> Dict[str, List[str]]:
    """
    Build skill synonyms mapping from database
    """
    try:
        all_skills = skill_repo.get_all_skills()
        synonyms_map = {}

        for skill_record in all_skills:
            skill_name = skill_record['skill_name'].lower()
            synonyms = skill_record.get('synonyms', [])

            if isinstance(synonyms, list):
                synonyms_map[skill_name] = [s.lower() for s in synonyms]
            else:
                synonyms_map[skill_name] = [skill_name]

        return {**SKILL_SYNONYMS, **synonyms_map}

    except Exception as e:
        print(f"Warning: Could not load skills from database: {e}")
        return SKILL_SYNONYMS

def normalize_skill_to_base(skill: str, synonyms_map: Dict[str, List[str]] = None) -> str:
    """Normalize skill to base form using database synonyms"""
    if not skill:
        return ""

    if synonyms_map is None:
        synonyms_map = SKILL_SYNONYMS

    skill_lower = skill.lower().strip()
    skill_lower = re.sub(r'[^\w\s]', '', skill_lower)
    skill_lower = re.sub(r'\s+', ' ', skill_lower)

    for base_skill, synonyms in synonyms_map.items():
        if skill_lower in synonyms or skill_lower == base_skill:
            return base_skill

    return skill_lower

def load_skill_dataset_from_db() -> Dict[str, List[str]]:
    """
    Load job roles and skills from database
    """
    try:
        skill_repo = SkillRepository()
        return skill_repo.get_all_job_roles()
    except Exception as e:
        print(f"Warning: Could not load roles from database: {e}")
        return {
            'Junior Data Scientist': ['Python', 'Pandas', 'Numpy', 'Data Visualization',
                                    'SQL', 'Statistics', 'Scikit-learn', 'EDA', 'Communication'],
            'Data Analyst': ['SQL', 'Excel', 'Data Visualization', 'Statistics',
                           'Reporting', 'Communication'],
        }

def parse_resume_structured(file_path: str) -> Dict[str, List[str]]:
    """Parse resume and return structured data"""
    try:
        result = parse_resume(file_path)

        if result and isinstance(result, dict):
            skills = result.get("skills", [])
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

def compute_skill_gap(
    resume_skills: List[str],
    required_skills: List[str],
    synonyms_map: Dict[str, List[str]] = None
) -> Dict[str, List[str]]:
    """Compute skill gap with proper normalization"""
    if synonyms_map is None:
        try:
            skill_repo = SkillRepository()
            synonyms_map = build_skill_synonyms_from_db(skill_repo)
        except:
            synonyms_map = SKILL_SYNONYMS

    normalized_resume = set()
    for skill in resume_skills:
        normalized = normalize_skill_to_base(skill, synonyms_map)
        if normalized:
            normalized_resume.add(normalized)

    skill_mapping = {}
    normalized_required = set()

    for skill in required_skills:
        normalized = normalize_skill_to_base(skill, synonyms_map)
        if normalized:
            normalized_required.add(normalized)
            skill_mapping[normalized] = skill

    matched_normalized = normalized_resume & normalized_required
    missing_normalized = normalized_required - normalized_resume

    matched = [skill_mapping[skill] for skill in matched_normalized]
    missing = [skill_mapping[skill] for skill in missing_normalized]

    return {"matched": matched, "missing": missing}

def analyze_resume(file_path: str, chosen_role: Optional[str] = None) -> Dict:
    """
    End-to-end resume analysis with database integration
    """
    roles_map = load_skill_dataset_from_db()
    structured = parse_resume_structured(file_path)

    print(f"DEBUG: Parsed skills: {structured.get('skills', [])}")

    skills_list = structured.get("skills", [])

    try:
        skill_repo = SkillRepository()
        synonyms_map = build_skill_synonyms_from_db(skill_repo)
    except:
        synonyms_map = SKILL_SYNONYMS

    predictions = []
    for role, required_skills in roles_map.items():
        gap_result = compute_skill_gap(skills_list, required_skills, synonyms_map)
        match_score = (len(gap_result["matched"]) / len(required_skills)) * 100 if required_skills else 0
        predictions.append((role, match_score))

    predictions.sort(key=lambda x: x[1], reverse=True)

    if chosen_role is None:
        chosen_role = predictions[0][0] if predictions else next(iter(roles_map.keys()))

    required = roles_map.get(chosen_role, [])

    gap = compute_skill_gap(skills_list, required, synonyms_map)

    total = len(required)
    score = (len(gap["matched"]) / total) * 100 if total > 0 else 0.0

    return {
        "parsed": structured,
        "predictions": predictions[:3],
        "chosen_role": chosen_role,
        "required_skills": required,
        "gap": gap,
        "match_score": score
    }
