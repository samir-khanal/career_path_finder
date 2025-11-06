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
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.pipeline import Pipeline

from src.parsing.ml.skill_matcher import load_skill_dataset, MODELS_DIR, MODEL_PATH, VECT_PATH

def synthesize_realistic_samples(roles_map: Dict[str, List[str]], per_role: int = 20) -> List[dict]:
    """
    Create realistic synthetic resumes with skill overlap between roles
    """
    rng = np.random.default_rng(7)
    samples: List[dict] = []
    
    # Common skills that appear across multiple roles (creates realistic overlap)
    common_skills = [
        "Python", "SQL", "Git", "Communication", "Problem Solving", 
        "Project Management", "Data Analysis", "Debugging", "Documentation",
        "Team Collaboration", "Agile Methodology", "Testing"
    ]
    
    for role, skills in roles_map.items():
        if len(skills) < 3:
            print(f" Skipping role '{role}' - only {len(skills)} skills available")
            continue
            
        for i in range(per_role):
            # Mix role-specific skills with common skills
            k_specific = rng.integers(low=3, high=min(8, len(skills)))
            k_common = rng.integers(low=1, high=4)  # Always include some common skills
            
            chosen_specific = rng.choice(skills, size=k_specific, replace=False)
            chosen_common = rng.choice(common_skills, size=k_common, replace=False)
            
            all_skills = list(chosen_specific) + list(chosen_common)
            rng.shuffle(all_skills)
            
            # Create realistic resume text WITHOUT role name
            text = (
                f"Professional with strong skills in {', '.join(all_skills[:3])}. "
                f"Experienced in {all_skills[3] if len(all_skills) > 3 else all_skills[0]} "
                f"and {all_skills[4] if len(all_skills) > 4 else all_skills[1]}. "
                f"Proven ability to deliver successful projects and solutions."
            )
            samples.append({"text": text, "label": role})
    
    return samples

def evaluate_model(X_train, X_test, y_train, y_test, vect, clf):
    """Comprehensive model evaluation"""
    # Transform data
    X_train_vec = vect.fit_transform(X_train)
    X_test_vec = vect.transform(X_test)
    
    # Train model
    clf.fit(X_train_vec, y_train)
    
    # Predictions
    y_pred = clf.predict(X_test_vec)
    
    # Calculate accuracy
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Test Accuracy: {accuracy:.4f}")
    print(f"Training samples: {len(X_train)}, Test samples: {len(X_test)}")
    print(f"Number of classes: {len(set(y_train))}")
    
    # Detailed classification report
    print("\n" + "="*50)
    print("CLASSIFICATION REPORT")
    print("="*50)
    print(classification_report(y_test, y_pred, zero_division=0))
    
    # Confusion matrix (small version for readability)
    print("\n" + "="*50)
    print("CONFUSION MATRIX (First 10 classes)")
    print("="*50)
    
    # Get unique labels and show first 10 for readability
    unique_labels = sorted(set(y_test))
    display_labels = unique_labels[:10]
    
    # Filter predictions for displayed labels
    mask = [y_true in display_labels and y_pred in display_labels 
            for y_true, y_pred in zip(y_test, y_pred)]
    
    y_test_filtered = [y_test[i] for i in range(len(y_test)) if mask[i]]
    y_pred_filtered = [y_pred[i] for i in range(len(y_pred)) if mask[i]]
    
    if y_test_filtered and y_pred_filtered:
        cm = confusion_matrix(y_test_filtered, y_pred_filtered, labels=display_labels)
        print("Labels:", display_labels)
        print("Confusion Matrix:")
        print(cm)
    else:
        print("Not enough samples for confusion matrix display")
    
    return accuracy, X_train_vec, X_test_vec

def cross_validate_model(texts, labels):
    """Perform cross-validation for more reliable evaluation"""
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=5000)),
        ('clf', LogisticRegression(max_iter=1000, random_state=42))
    ])
    
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(pipeline, texts, labels, cv=cv, scoring='accuracy')
    
    print("\n" + "="*50)
    print("CROSS-VALIDATION RESULTS")
    print("="*50)
    print(f"Fold scores: {[f'{s:.4f}' for s in scores]}")
    print(f"Mean CV Accuracy: {scores.mean():.4f} (±{scores.std():.4f})")
    
    return scores

def train_and_save(per_role: int = 25) -> None:
    """Main training function with proper evaluation"""
    
    # Load role skills
    roles_map = load_skill_dataset()
    
    # DEBUG: Check what's loaded
    print("Loaded roles and skill counts:")
    for role, skills in roles_map.items():
        print(f"  {role}: {len(skills)} skills")
    
    # Generate realistic samples
    samples = synthesize_realistic_samples(roles_map, per_role=per_role)
    
    if not samples:
        raise ValueError(" No samples generated! Check if any roles have sufficient skills.")
    
    print(f"\nGenerated {len(samples)} training samples")
    print(f"Number of unique roles: {len(set(s['label'] for s in samples))}")
    
    texts = [s["text"] for s in samples]
    labels = [s["label"] for s in samples]
    
    # Show sample of generated texts (for verification)
    print("\n" + "="*50)
    print("SAMPLE GENERATED TEXTS (First 3)")
    print("="*50)
    for i in range(min(3, len(texts))):
        print(f"Text: {texts[i]}")
        print(f"Label: {labels[i]}")
        print("---")
    
    # Perform cross-validation first
    cv_scores = cross_validate_model(texts, labels)
    
    # Now train final model with train-test split
    print("\n" + "="*50)
    print("FINAL MODEL TRAINING")
    print("="*50)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, 
        test_size=0.3, 
        random_state=42, 
        stratify=labels
    )
    
    # Initialize vectorizer and classifier
    vect = TfidfVectorizer(
        ngram_range=(1, 2), 
        min_df=2,  # Increased to ignore very rare terms
        max_features=5000,
        stop_words='english'
    )
    
    clf = LogisticRegression(
        max_iter=1000,
        random_state=42,
        C=1.0
    )
    
    # Train and evaluate
    accuracy, X_train_vec, X_test_vec = evaluate_model(X_train, X_test, y_train, y_test, vect, clf)
    
    # Save the model only if accuracy is realistic (not 100%)
    if accuracy < 0.95:  # Reasonable threshold
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(clf, MODEL_PATH)
        joblib.dump(vect, VECT_PATH)
        
        print(f"\n✅ Model saved successfully!")
        print(f"   Model -> {MODEL_PATH}")
        print(f"   Vectorizer -> {VECT_PATH}")
        print(f"   Realistic accuracy: {accuracy:.4f}")
    else:
        print(f"\n❌ Model not saved - suspicious accuracy: {accuracy:.4f}")
        print("   Check for data leakage or insufficient variation in samples")
    
    # Show most important features for some classes
    print("\n" + "="*50)
    print("FEATURE ANALYSIS (Sample)")
    print("="*50)
    
    try:
        feature_names = vect.get_feature_names_out()
        for i, class_name in enumerate(clf.classes_[:3]):  # First 3 classes
            coefs = clf.coef_[i]
            top_indices = np.argsort(coefs)[-5:]  # Top 5 features
            top_features = [feature_names[idx] for idx in top_indices]
            print(f"Top features for '{class_name}': {top_features}")
    except Exception as e:
        print(f"Feature analysis skipped: {e}")

if __name__ == "__main__":
    train_and_save(per_role=25)