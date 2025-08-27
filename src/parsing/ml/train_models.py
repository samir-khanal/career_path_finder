# src/parsing/ml/train_models.py
from __future__ import annotations
from pathlib import Path
from typing import Dict, List
import numpy as np
import joblib
import sys

# Add the project root to Python path
project_root = Path(__file__).resolve().parents[3]
sys.path.append(str(project_root))

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from src.parsing.ml.skill_matcher import load_skill_dataset, MODELS_DIR, MODEL_PATH, VECT_PATH

def synthesize_samples(roles_map: Dict[str, List[str]], per_role: int = 12) -> List[dict]:
    """
    Creates tiny synthetic 'resume-like' texts using each role's skills.
    This is only to bootstrap a demo model. Replace with real data when you can.
    """
    rng = np.random.default_rng(7)
    samples: List[dict] = []
    
    for role, skills in roles_map.items():
        # Skip roles with insufficient skills
        if len(skills) < 3:
            print(f"⚠️ Skipping role '{role}' - only {len(skills)} skills available")
            continue
            
        for i in range(per_role):
            # FIXED: Ensure low < high for random sampling
            low_val = max(3, len(skills) // 2)  # Reduced from 5 to 3
            high_val = len(skills) + 1
            
            # Safety check: ensure low < high
            if low_val >= high_val:
                low_val = high_val - 1  # Force low to be less than high
                
            k = rng.integers(low=low_val, high=high_val)
            chosen = rng.choice(skills, size=min(k, len(skills)), replace=False)
            text = (
                f"Experienced {role}. "
                f"Key skills: {', '.join(chosen)}. "
                f"Projects used {chosen[0]} and {chosen[-1]}."
            )
            samples.append({"text": text, "label": role})
    
    return samples

def train_and_save(per_role: int = 12) -> None:
    roles_map = load_skill_dataset()
    
    # DEBUG: Check what's loaded
    print("🔍 Loaded roles and skill counts:")
    for role, skills in roles_map.items():
        print(f"  {role}: {len(skills)} skills")
        if len(skills) < 3:
            print(f"    ❌ WARNING: Only {len(skills)} skills - may cause issues")
    
    samples = synthesize_samples(roles_map, per_role=per_role)
    
    if not samples:
        raise ValueError("❌ No samples generated! Check if any roles have sufficient skills.")
    
    print(f"✅ Generated {len(samples)} training samples")
    
    texts = [s["text"] for s in samples]
    labels = [s["label"] for s in samples]

    vect = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    X = vect.fit_transform(texts)

    clf = LogisticRegression(max_iter=500)
    clf.fit(X, labels)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(clf, MODEL_PATH)
    joblib.dump(vect, VECT_PATH)

    print(f"✅ Saved model -> {MODEL_PATH}")
    print(f"✅ Saved vectorizer -> {VECT_PATH}")
    print(f"✅ Training complete! Model trained on {len(set(labels))} roles")

if __name__ == "__main__":
    train_and_save(per_role=12)