# src/parsing/ml/evaluate_model.py
"""
Standalone Model Evaluation Script
Purpose: Generate accuracy metrics for presentation purposes
Note: This script is NOT connected to the main application
      It's for demonstrating ML capabilities to stakeholders
"""

from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import joblib
import sys
import json
from datetime import datetime

# Add the project root to Python path
project_root = Path(__file__).resolve().parents[3]
sys.path.append(str(project_root))

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score, 
    precision_score, 
    recall_score, 
    f1_score,
    classification_report,
    confusion_matrix,
    roc_auc_score
)
import pandas as pd

from src.parsing.ml.skill_matcher import load_skill_dataset, MODELS_DIR, MODEL_PATH, VECT_PATH

# Output directory for metrics
METRICS_DIR = MODELS_DIR / "evaluation_metrics"
METRICS_DIR.mkdir(parents=True, exist_ok=True)

METRICS_JSON = METRICS_DIR / "model_metrics.json"
METRICS_REPORT = METRICS_DIR / "evaluation_report.txt"
CONFUSION_CSV = METRICS_DIR / "confusion_matrix.csv"


def synthesize_samples(roles_map: Dict[str, List[str]], per_role: int = 20) -> List[dict]:
    """
    Creates REALISTIC synthetic 'resume-like' texts with skill overlaps
    """
    rng = np.random.default_rng(42)
    samples: List[dict] = []
    
    print("\n Generating Synthetic Training Data...")
    print("=" * 60)
    
    # Realistic templates WITHOUT job titles
    templates = [
        "Strong background in {skills}. Experienced with {primary_skill}.",
        "Proficient in {skills}. Recent projects involved {random_skill}.",
        "Technical skills include {skills}. Hands-on experience with {primary_skill}.",
        "Skilled in {skills}. Demonstrated success with {random_skill} implementations.",
        "Expertise in {skills}. Strong capabilities in {primary_skill} applications.",
        "Technical professional experienced in {skills}.",
        "Competencies include {skills}. Proven track record with {random_skill}."
    ]
    
    for role, skills in roles_map.items():
        if len(skills) < 3:
            print(f"  Skipping '{role}' - only {len(skills)} skills (need ≥3)")
            continue
            
        role_samples = 0
        for i in range(per_role):
            # Select 3-6 skills randomly (not all skills)
            num_skills = rng.integers(3, min(7, len(skills) + 1))
            chosen_skills = rng.choice(skills, size=num_skills, replace=False)
            
            # Format skills naturally
            if len(chosen_skills) > 1:
                skills_text = ', '.join(chosen_skills[:-1]) + ' and ' + chosen_skills[-1]
            else:
                skills_text = chosen_skills[0]
            
            primary_skill = chosen_skills[0]
            random_skill = rng.choice(chosen_skills)
            
            # Choose template and generate text
            template = rng.choice(templates)
            text = template.format(
                skills=skills_text,
                primary_skill=primary_skill,
                random_skill=random_skill
            )
            
            samples.append({"text": text, "label": role})
            role_samples += 1
        
        print(f"✓ {role:25} → {role_samples:2} samples ({len(skills)} skills)")
    
    print("=" * 60)
    print(f" Total samples generated: {len(samples)}\n")
    return samples

def train_and_evaluate_model(per_role: int = 20, test_size: float = 0.25) -> Dict:
    """
    Train model and generate comprehensive evaluation metrics
    
    Args:
        per_role: Number of samples per job role
        test_size: Proportion of data for testing (default 25%)
    
    Returns:
        Dictionary containing all evaluation metrics
    """
    print("\n" + "=" * 60)
    print(" RESUME ANALYZER - MODEL EVALUATION")
    print("=" * 60)
    
    # Load job roles and skills from database
    print("\n[1/6] Loading job roles from database...")
    roles_map = load_skill_dataset()
    
    print(f"✓ Loaded {len(roles_map)} job roles")
    print("\nJob Roles:")
    for role, skills in roles_map.items():
        print(f"  • {role:30} ({len(skills):2} skills)")
    
    # Generate synthetic data
    print("\n[2/6] Generating synthetic training data...")
    samples = synthesize_samples(roles_map, per_role=per_role)
    
    if not samples:
        raise ValueError(" No samples generated! Check if roles have sufficient skills.")
    
    texts = [s["text"] for s in samples]
    labels = [s["label"] for s in samples]
    
    # Split data
    print(f"\n[3/6] Splitting data (train: {int((1-test_size)*100)}%, test: {int(test_size*100)}%)...")
    X_train_text, X_test_text, y_train, y_test = train_test_split(
        texts, labels, test_size=test_size, random_state=42, stratify=labels
    )
    
    print(f"✓ Training samples: {len(X_train_text)}")
    print(f"✓ Testing samples: {len(X_test_text)}")
    
    # Vectorization
    print("\n[4/6] Vectorizing text data (TF-IDF)...")
    vect = TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=500)
    X_train = vect.fit_transform(X_train_text)
    X_test = vect.transform(X_test_text)
    
    print(f"✓ Feature dimensions: {X_train.shape[1]}")
    
    # Train model
    print("\n[5/6] Training Logistic Regression model...")
    clf = LogisticRegression(max_iter=1000, random_state=42, solver='lbfgs')
    clf.fit(X_train, y_train)
    
    print("✓ Model training complete")
    
    # Predictions
    print("\n[6/6] Generating predictions and metrics...")
    y_pred = clf.predict(X_test)
    y_pred_proba = clf.predict_proba(X_test)
    
    # Calculate metrics
    metrics = {
        "model_info": {
            "algorithm": "Logistic Regression",
            "features": "TF-IDF (1-2 ngrams)",
            "max_features": 500,
            "training_samples": len(X_train_text),
            "testing_samples": len(X_test_text),
            "num_classes": len(set(labels)),
            "classes": sorted(list(set(labels))),
            "evaluation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        "overall_metrics": {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision_weighted": float(precision_score(y_test, y_pred, average='weighted', zero_division=0)),
            "recall_weighted": float(recall_score(y_test, y_pred, average='weighted', zero_division=0)),
            "f1_score_weighted": float(f1_score(y_test, y_pred, average='weighted', zero_division=0)),
            "precision_macro": float(precision_score(y_test, y_pred, average='macro', zero_division=0)),
            "recall_macro": float(recall_score(y_test, y_pred, average='macro', zero_division=0)),
            "f1_score_macro": float(f1_score(y_test, y_pred, average='macro', zero_division=0))
        }
    }
    
    # Cross-validation scores
    print("  → Running cross-validation...")
    cv_scores = cross_val_score(clf, X_train, y_train, cv=5, scoring='accuracy')
    metrics["cross_validation"] = {
        "cv_scores": [float(s) for s in cv_scores],
        "cv_mean": float(cv_scores.mean()),
        "cv_std": float(cv_scores.std())
    }
    
    # Per-class metrics
    print("  → Calculating per-class metrics...")
    class_report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    
    metrics["per_class_metrics"] = {}
    for class_name, class_metrics in class_report.items():
        if class_name not in ['accuracy', 'macro avg', 'weighted avg']:
            metrics["per_class_metrics"][class_name] = {
                "precision": float(class_metrics['precision']),
                "recall": float(class_metrics['recall']),
                "f1-score": float(class_metrics['f1-score']),
                "support": int(class_metrics['support'])
            }
    
    # Confusion matrix
    print("  → Building confusion matrix...")
    cm = confusion_matrix(y_test, y_pred, labels=sorted(list(set(labels))))
    
    # Save confusion matrix as CSV
    cm_df = pd.DataFrame(
        cm,
        index=sorted(list(set(labels))),
        columns=sorted(list(set(labels)))
    )
    cm_df.to_csv(CONFUSION_CSV)
    
    # Save model
    print("\n Saving model and vectorizer...")
    joblib.dump(clf, MODEL_PATH)
    joblib.dump(vect, VECT_PATH)
    print(f"✓ Model saved: {MODEL_PATH}")
    print(f"✓ Vectorizer saved: {VECT_PATH}")
    
    return metrics


def save_metrics_report(metrics: Dict) -> None:
    """Save metrics to JSON and text report"""
    
    # Save JSON
    with open(METRICS_JSON, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"✓ Metrics JSON saved: {METRICS_JSON}")
    
    # Generate text report
    report_lines = []
    report_lines.append("=" * 70)
    report_lines.append("RESUME ANALYZER - MODEL EVALUATION REPORT")
    report_lines.append("=" * 70)
    report_lines.append("")
    
    # Model info
    report_lines.append("MODEL INFORMATION")
    report_lines.append("-" * 70)
    for key, value in metrics["model_info"].items():
        if key == "classes":
            report_lines.append(f"  {key:20}: {len(value)} classes")
        else:
            report_lines.append(f"  {key:20}: {value}")
    report_lines.append("")
    
    # Overall metrics
    report_lines.append("OVERALL PERFORMANCE METRICS")
    report_lines.append("-" * 70)
    overall = metrics["overall_metrics"]
    report_lines.append(f"  Accuracy:              {overall['accuracy']:.4f} ({overall['accuracy']*100:.2f}%)")
    report_lines.append(f"  Precision (Weighted):  {overall['precision_weighted']:.4f} ({overall['precision_weighted']*100:.2f}%)")
    report_lines.append(f"  Recall (Weighted):     {overall['recall_weighted']:.4f} ({overall['recall_weighted']*100:.2f}%)")
    report_lines.append(f"  F1-Score (Weighted):   {overall['f1_score_weighted']:.4f} ({overall['f1_score_weighted']*100:.2f}%)")
    report_lines.append("")
    report_lines.append(f"  Precision (Macro):     {overall['precision_macro']:.4f} ({overall['precision_macro']*100:.2f}%)")
    report_lines.append(f"  Recall (Macro):        {overall['recall_macro']:.4f} ({overall['recall_macro']*100:.2f}%)")
    report_lines.append(f"  F1-Score (Macro):      {overall['f1_score_macro']:.4f} ({overall['f1_score_macro']*100:.2f}%)")
    report_lines.append("")
    
    # Cross-validation
    report_lines.append("CROSS-VALIDATION RESULTS (5-Fold)")
    report_lines.append("-" * 70)
    cv = metrics["cross_validation"]
    report_lines.append(f"  Mean CV Accuracy:      {cv['cv_mean']:.4f} ± {cv['cv_std']:.4f}")
    report_lines.append(f"  Individual CV Scores:  {', '.join([f'{s:.4f}' for s in cv['cv_scores']])}")
    report_lines.append("")
    
    # Per-class metrics
    report_lines.append(" PER-CLASS PERFORMANCE")
    report_lines.append("-" * 70)
    report_lines.append(f"{'Class':<35} {'Precision':<12} {'Recall':<12} {'F1-Score':<12} {'Support':<10}")
    report_lines.append("-" * 70)
    
    for class_name, class_metrics in metrics["per_class_metrics"].items():
        report_lines.append(
            f"{class_name:<35} "
            f"{class_metrics['precision']:<12.4f} "
            f"{class_metrics['recall']:<12.4f} "
            f"{class_metrics['f1-score']:<12.4f} "
            f"{class_metrics['support']:<10}"
        )
    
    report_lines.append("")
    report_lines.append("=" * 70)
    report_lines.append("INTERPRETATION GUIDE")
    report_lines.append("=" * 70)
    report_lines.append("• Accuracy:   Overall correctness of predictions")
    report_lines.append("• Precision:  Of predicted positives, how many were correct")
    report_lines.append("• Recall:     Of actual positives, how many were detected")
    report_lines.append("• F1-Score:   Harmonic mean of precision and recall")
    report_lines.append("• Support:    Number of samples in each class")
    report_lines.append("")
    report_lines.append("Weighted: Accounts for class imbalance")
    report_lines.append("Macro:    Simple average across all classes")
    report_lines.append("=" * 70)
    
     # Save report with UTF-8 encoding
    with open(METRICS_REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    print(f"✓ Text report saved: {METRICS_REPORT}")


def print_summary(metrics: Dict) -> None:
    """Print a summary of key metrics to console"""
    print("\n" + "=" * 60)
    print(" MODEL EVALUATION COMPLETE")
    print("=" * 60)
    
    overall = metrics["overall_metrics"]
    cv = metrics["cross_validation"]
    
    print("\n KEY METRICS FOR PRESENTATION:")
    print("-" * 60)
    print(f"  Accuracy:          {overall['accuracy']*100:.2f}%")
    print(f"  Precision:         {overall['precision_weighted']*100:.2f}%")
    print(f"  Recall:            {overall['recall_weighted']*100:.2f}%")
    print(f"  F1-Score:          {overall['f1_score_weighted']*100:.2f}%")
    print(f"  CV Accuracy:       {cv['cv_mean']*100:.2f}% ± {cv['cv_std']*100:.2f}%")
    print("-" * 60)
    
    print("\n OUTPUT FILES:")
    print(f"  • Metrics JSON:       {METRICS_JSON}")
    print(f"  • Evaluation Report:  {METRICS_REPORT}")
    print(f"  • Confusion Matrix:   {CONFUSION_CSV}")
    print(f"  • Trained Model:      {MODEL_PATH}")
    print(f"  • Vectorizer:         {VECT_PATH}")
    
    print("\n USAGE FOR PRESENTATION:")
    print("  1. Show overall accuracy and F1-score from above")
    print("  2. Open evaluation_report.txt for detailed breakdown")
    print("  3. Reference confusion_matrix.csv for class-wise analysis")
    print("  4. Emphasize: 'Model achieves {:.0f}% accuracy on test data'".format(overall['accuracy']*100))
    print("\n" + "=" * 60 + "\n")


def main():
    """Main execution function"""
    try:
        # Train and evaluate model
        metrics = train_and_evaluate_model(per_role=20, test_size=0.25)
        
        # Save detailed reports
        save_metrics_report(metrics)
        
        # Print summary
        print_summary(metrics)
        
        print(" All done! Check the output files in:")
        print(f"   {METRICS_DIR}\n")
        
    except Exception as e:
        print(f"\n❌ Error during evaluation: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()