# src/ml/skill_matcher.py
from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json
import joblib
import re

# --- Import your existing parsing layer ---
from src.parsing import parse_resume
try:
    from src.parsing.resume_parser import extract_resume_info
except Exception:
    extract_resume_info = None

# ----------------------------
# Paths
# ----------------------------
PROJ_ROOT = Path(__file__).resolve().parents[3]
MODELS_DIR = PROJ_ROOT / "models"
DATASET_CSV = MODELS_DIR / "skills_dataset.csv"
MODEL_PATH = MODELS_DIR / "trained_model.pkl"
VECT_PATH  = MODELS_DIR / "vectorizer.pkl"

# ----------------------------
# Skill Synonyms Mapping
# ----------------------------
SKILL_SYNONYMS = {
    # -------------------- Programming Languages --------------------
    "python": ["python", "py", "python3", "python programming"],
    "java": ["java", "java programming", "jdk", "j2ee"],
    "javascript": ["javascript", "js", "ecmascript", "nodejs", "node.js"],
    "typescript": ["typescript", "ts"],
    "c++": ["c++", "cpp", "c plus plus"],
    "c#": ["c#", "c sharp", ".net c#"],
    "php": ["php", "php7", "laravel php"],
    "r": ["r", "r programming", "r-lang"],
    "kotlin": ["kotlin", "android kotlin"],
    "swift": ["swift", "ios swift"],
    
    # -------------------- Data Science & ML --------------------
    "machine learning": ["machine learning", "ml", "ai", "ml modeling", "predictive modeling"],
    "deep learning": ["deep learning", "dl", "neural networks", "cnn", "rnn", "transformers"],
    "nlp": ["nlp", "natural language processing", "text mining", "spacy", "nltk"],
    "data analysis": ["data analysis", "data analytics", "analytics", "business analysis"],
    "data visualization": ["data visualization", "visualization", "charts", "dashboards"],
    "pandas": ["pandas", "data manipulation", "dataframe"],
    "numpy": ["numpy", "numerical computing", "linear algebra"],
    "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
    "tensorflow": ["tensorflow", "tf", "tf2"],
    "keras": ["keras", "tf-keras"],
    "pytorch": ["pytorch", "torch"],
    "tableau": ["tableau", "tableau desktop", "tableau prep"],
    "power bi": ["powerbi", "power bi", "ms powerbi"],
    "eda": ["eda", "exploratory data analysis"],
    
    # -------------------- Databases --------------------
    "sql": ["sql", "mysql", "postgresql", "postgres", "mssql", "oracle sql", "sqlite", "pl/sql"],
    "nosql": ["nosql", "mongodb", "cassandra", "dynamodb", "couchdb"],
    "database": ["database", "dbms", "db admin", "oracle", "rdbms"],
    
    # -------------------- Cloud & DevOps --------------------
    "aws": ["aws", "amazon web services", "ec2", "s3", "lambda", "cloudwatch"],
    "azure": ["azure", "microsoft azure", "azure cloud"],
    "gcp": ["gcp", "google cloud", "google cloud platform"],
    "docker": ["docker", "docker containers"],
    "kubernetes": ["kubernetes", "k8s", "kube"],
    "jenkins": ["jenkins", "ci/cd", "continuous integration"],
    "terraform": ["terraform", "iac", "infrastructure as code"],
    "linux": ["linux", "ubuntu", "redhat", "debian", "centos"],
    "git": ["git", "github", "gitlab", "bitbucket", "version control"],
    
    # -------------------- Web Development --------------------
    "html": ["html", "html5"],
    "css": ["css", "css3", "tailwind", "bootstrap"],
    "react": ["react", "react.js", "reactjs", "react native"],
    "angular": ["angular", "angularjs"],
    "vue": ["vue", "vue.js", "vuejs"],
    "node": ["node", "nodejs", "node.js"],
    "express": ["express", "expressjs"],
    "django": ["django", "django rest", "drf"],
    "flask": ["flask", "flask api"],
    "spring": ["spring", "spring boot", "spring framework"],
    
    # -------------------- Mobile Development --------------------
    "android": ["android", "android studio"],
    "ios": ["ios", "apple ios", "swift ios"],
    "flutter": ["flutter", "dart", "flutter sdk"],
    "react native": ["react native", "rn mobile"],
    
    # -------------------- Cybersecurity --------------------
    "cybersecurity": ["cybersecurity", "information security", "infosec"],
    "network security": ["network security", "firewalls", "ids/ips"],
    "ethical hacking": ["ethical hacking", "penetration testing", "pentesting", "bug bounty"],
    "cryptography": ["cryptography", "crypto algorithms", "ssl/tls"],
    "siem": ["siem", "splunk", "security monitoring"],
    
    # -------------------- UI/UX --------------------
    "ui design": ["ui design", "user interface", "interface design"],
    "ux design": ["ux design", "user experience", "interaction design"],
    "figma": ["figma", "figma design"],
    "adobe xd": ["adobe xd", "xd"],
    "photoshop": ["photoshop", "adobe photoshop"],
    "illustrator": ["illustrator", "adobe illustrator"],
    "wireframing": ["wireframing", "mockups", "prototyping"],
    
    # -------------------- Soft Skills --------------------
    "communication": ["communication", "comm skills", "presentation skills"],
    "problem solving": ["problem solving", "troubleshooting", "analytical thinking"],
    "teamwork": ["teamwork", "collaboration", "working in teams"],
    "leadership": ["leadership", "team lead", "management"],
    "critical thinking": ["critical thinking", "logical thinking", "reasoning"],
}


def get_skill_synonyms(skill: str) -> List[str]:
    """Get all synonyms for a given skill"""
    skill_lower = skill.lower().strip()
    for base_skill, synonyms in SKILL_SYNONYMS.items():
        if skill_lower in synonyms or skill_lower == base_skill:
            return synonyms
    return [skill_lower]

def normalize_skill_to_base(skill: str) -> str:
    """Normalize skill to base form using the comprehensive SKILL_SYNONYMS"""
    if not skill:
        return ""
    
    # Convert to lowercase and clean
    skill_lower = skill.lower().strip()
    skill_lower = re.sub(r'[^\w\s]', '', skill_lower)  # Remove punctuation
    skill_lower = re.sub(r'\s+', ' ', skill_lower)     # Normalize whitespace
    
    # Use your comprehensive SKILL_SYNONYMS instead of the small synonym_mapping
    for base_skill, synonyms in SKILL_SYNONYMS.items():
        if skill_lower in synonyms or skill_lower == base_skill:
            return base_skill
    
    return skill_lower

def debug_skill_matching(resume_skills: List[str], required_skills: List[str]):
    """Debug function to see skill matching process"""
    print("=== DEBUG SKILL MATCHING ===")
    print(f"Original resume skills: {resume_skills}")
    print(f"Original required skills: {required_skills}")
    
    # Show normalization
    normalized_resume = [normalize_skill_to_base(s) for s in resume_skills]
    normalized_required = [normalize_skill_to_base(s) for s in required_skills]
    
    print(f"Normalized resume: {normalized_resume}")
    print(f"Normalized required: {normalized_required}")
    
    # Show matching
    matched = set(normalized_resume) & set(normalized_required)
    missing = set(normalized_required) - set(normalized_resume)
    
    print(f"Matched: {matched}")
    print(f"Missing: {missing}")
    print("========================")

def debug_normalization_examples():
    """Show examples of skill normalization"""
    print("=== SKILL NORMALIZATION EXAMPLES ===")
    test_skills = ["Python", "ML", "Sql", "Data Visualization", "Pandas", "React.js"]
    
    for skill in test_skills:
        normalized = normalize_skill_to_base(skill)
        print(f"'{skill}' -> '{normalized}'")
    
    print("========================")

# ----------------------------
# Data loaders
# ----------------------------
def load_skill_dataset(csv_path: Path = DATASET_CSV) -> Dict[str, List[str]]:
    """Load CSV with skills dataset - COMPLETELY FIXED VERSION"""
    if not csv_path.exists():
        raise FileNotFoundError(f"skills_dataset.csv not found at {csv_path}")

    roles: Dict[str, List[str]] = {}
    
    try:
        # Use pandas for reliable CSV parsing
        import pandas as pd
        df = pd.read_csv(csv_path)
        
        print(f"✅ CSV loaded successfully with {len(df)} rows")
        
        for _, row in df.iterrows():
            role = row['role']
            skills_str = row['skills']
            
            # Split skills by semicolon and clean
            skills = [s.strip() for s in skills_str.split(';') if s.strip()]
            
            if not skills:
                print(f"⚠️ Warning: Role '{role}' has no skills in CSV")
                continue
                
            roles[role] = skills
            
        return roles
            
    except Exception as e:
        print(f"❌ Error with pandas: {e}")
        print("Trying manual CSV parsing...")
        
        # Manual CSV parsing as fallback
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
                # Check if first line is header
                if 'role' in lines[0].lower() and 'skills' in lines[0].lower():
                    lines = lines[1:]  # Skip header
                
                for line in lines:
                    if not line.strip() or line.strip().startswith('#'):
                        continue
                    
                    # Handle different separators
                    if ';' in line:
                        parts = line.strip().split(';', 1)
                    else:
                        parts = line.strip().split(',', 1)
                        
                    if len(parts) < 2:
                        continue
                        
                    role = parts[0].strip()
                    skills_str = parts[1].strip().strip('"\'')  # Remove quotes
                    
                    # Clean skills list
                    skills = [s.strip() for s in skills_str.split(';') if s.strip()]
                    
                    if not skills:
                        print(f"⚠️ Warning: Role '{role}' has no skills")
                        continue
                        
                    roles[role] = skills
                    
            print(f"✅ Manual parsing loaded {len(roles)} roles")
            return roles
                    
        except Exception as e2:
            print(f"❌ Error reading CSV: {e2}")
            raise

# ----------------------------
# Resume parsing helpers
# ----------------------------
def _naive_extract_from_raw(text: str, roles_map: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Fallback extractor"""
    lower = text.lower()
    vocab = {s.lower() for skills in roles_map.values() for s in skills}
    found_skills = sorted({s for s in vocab if s in lower}, key=str.lower)
    found_skills = [s.title() for s in found_skills]

    def grab(section: str) -> List[str]:
        m = re.search(rf"{section}[:\-]?\s*(.*)", lower)
        return [m.group(1)] if m else []

    return {
        "skills": found_skills,
        "education": grab("education"),
        "experience": grab("experience"),
    }

def parse_resume_structured(file_path: str) -> Dict[str, List[str]]:
    """Parse resume and return structured data - FIXED VERSION"""
    try:
        # Use your updated parser from src.parsing
        result = parse_resume(file_path)
        
        if result and isinstance(result, dict):
            # Ensure skills is always a list (not a string)
            skills = result.get("skills", [])
            if isinstance(skills, str):
                skills = [skills]
            
            # Handle case where skills might be in a single string
            if skills and len(skills) == 1 and isinstance(skills[0], str):
                # Split combined skills string
                combined_skills = skills[0]
                skills = split_skills_string(combined_skills)
            
            return {
                "skills": skills,
                "education": result.get("education", []),
                "experience": result.get("experience", [])
            }
        
        return {"skills": [], "education": [], "experience": []}
        
    except Exception as e:
        print(f"Error in parse_resume_structured: {e}")
        return {"skills": [], "education": [], "experience": []}
    
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
        # If no delimiters, try to split by spaces (but be smart about it)
        # Handle "Python Machine Learning SQL" pattern
        skills = re.split(r'\s{2,}', skills_text)  # Split on multiple spaces first
        skills = [skill.strip() for skill in skills if skill.strip()]
        
        # If still not split properly, try more aggressive splitting
        if len(skills) <= 1:
            # Split on single spaces but only if they look like skill boundaries
            skills = re.findall(r'[A-Z][a-z]+|[A-Z]+|[a-z]+', skills_text)
            skills = [skill.strip() for skill in skills if skill.strip() and len(skill) > 2]
    
    return skills
# ----------------------------
# Matching & predictions
# ----------------------------
def compute_skill_gap(resume_skills: List[str], required_skills: List[str]) -> Dict[str, List[str]]:
    """
    Compute skill gap with proper normalization
    """
    # Normalize resume skills
    normalized_resume = set()
    for skill in resume_skills:
        normalized = normalize_skill_to_base(skill)
        if normalized:
            normalized_resume.add(normalized)
    
    # Normalize required skills and create mapping
    skill_mapping = {}  # Map normalized to original for display
    normalized_required = set()
    
    for skill in required_skills:
        normalized = normalize_skill_to_base(skill)
        if normalized:
            normalized_required.add(normalized)
            skill_mapping[normalized] = skill  # Map to original name
    
    # Find matches
    matched_normalized = normalized_resume & normalized_required
    missing_normalized = normalized_required - normalized_resume
    
    # Convert back to original skill names
    matched = [skill_mapping[skill] for skill in matched_normalized]
    missing = [skill_mapping[skill] for skill in missing_normalized]
    
    return {"matched": matched, "missing": missing}

def load_model() -> Tuple[Optional[object], Optional[object]]:
    if MODEL_PATH.exists() and VECT_PATH.exists():
        return joblib.load(MODEL_PATH), joblib.load(VECT_PATH)
    return None, None

def predict_roles(text: str, top_k: int = 3) -> List[Tuple[str, float]]:
    """Predict top-k roles using trained model"""
    model, vect = load_model()
    if model is None or vect is None:
        return []

    if not text.strip():
        return []

    X = vect.transform([text])
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)[0]
        idxs = proba.argsort()[::-1][:top_k]
        roles = list(model.classes_)
        return [(roles[i], float(proba[i])) for i in idxs]

    # Fallback to decision_function ranking
    scores = model.decision_function(X)[0]
    idxs = scores.argsort()[::-1][:top_k]
    roles = list(model.classes_)
    import numpy as np
    scores = scores - scores.min()
    probs = scores / scores.sum() if scores.sum() > 0 else np.ones_like(scores) / len(scores)
    return [(roles[i], float(probs[i])) for i in idxs]

def analyze_resume(file_path: str, chosen_role: Optional[str] = None) -> Dict:
    """End-to-end resume analysis with debug info - FIXED VERSION"""
    roles_map = load_skill_dataset()
    structured = parse_resume_structured(file_path)

    # DEBUG: Show what was parsed
    print(f"DEBUG: Parsed skills: {structured.get('skills', [])}")
    print(f"DEBUG: Skills type: {type(structured.get('skills', []))}")
    print(f"DEBUG: Skills count: {len(structured.get('skills', []))}")
    
    # Ensure skills is a list and handle single string case
    skills_list = structured.get("skills", [])
    if isinstance(skills_list, str):
        skills_list = [skills_list]
    
    # Handle case where all skills are in a single string
    if skills_list and len(skills_list) == 1 and isinstance(skills_list[0], str):
        print("DEBUG: Splitting combined skills string")
        skills_list = split_skills_string(skills_list[0])
        print(f"DEBUG: After splitting: {skills_list}")

    blob = " ".join(structured.get("education", []) + structured.get("experience", []) + skills_list)

    preds = predict_roles(blob, top_k=3)
    if chosen_role is None:
        chosen_role = preds[0][0] if preds else next(iter(roles_map.keys()))

    required = roles_map.get(chosen_role, [])
    
    # DEBUG: Show matching process
    print(f"DEBUG: Required skills for {chosen_role}: {required}")
    debug_skill_matching(skills_list, required)
    
    gap = compute_skill_gap(skills_list, required)

    total = len(required)
    score = (len(gap["matched"]) / total) * 100 if total > 0 else 0.0

    return {
        "parsed": structured,
        "predictions": preds,
        "chosen_role": chosen_role,
        "required_skills": required,
        "gap": gap,
        "match_score": score
    }