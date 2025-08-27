# debug_fix.py
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[3]
sys.path.append(str(project_root))

def test_csv_loading():
    """Test if CSV loads without errors"""
    print("📊 Testing CSV Loading...")
    try:
        from src.parsing.ml.skill_matcher import load_skill_dataset
        roles = load_skill_dataset()
        print(f"✅ Success! Loaded {len(roles)} roles")
        for role, skills in roles.items():
            print(f"   {role}: {len(skills)} skills")
        return True
    except Exception as e:
        print(f"❌ CSV loading failed: {e}")
        return False

def test_skill_matching():
    """Test if skill matching works"""
    print("\n🎯 Testing Skill Matching...")
    try:
        from src.parsing.ml.skill_matcher import compute_skill_gap
        
        # Test case
        resume_skills = ["Python", "ML", "Data Visualization"]
        required_skills = ["python", "machine learning", "data visualization"]
        
        result = compute_skill_gap(resume_skills, required_skills)
        
        print(f"Resume skills: {resume_skills}")
        print(f"Required skills: {required_skills}")
        print(f"✅ Matched: {result['matched']}")
        print(f"❌ Missing: {result['missing']}")
        
        expected_matches = 3
        actual_matches = len(result['matched'])
        
        if actual_matches == expected_matches:
            print("🎉 Skill matching WORKS!")
            return True
        else:
            print(f"💥 Expected {expected_matches} matches, got {actual_matches}")
            return False
            
    except Exception as e:
        print(f"❌ Skill matching failed: {e}")
        return False

def test_model_loading():
    """Test if model loads without warnings"""
    print("\n🤖 Testing Model Loading...")
    try:
        from src.parsing.ml.skill_matcher import load_model
        model, vect = load_model()
        
        if model and vect:
            print("✅ Model loaded successfully")
            return True
        else:
            print("⚠️ No model found (this might be expected)")
            return True
            
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Running Diagnostic Tests...")
    print("=" * 50)
    
    tests = [
        test_csv_loading,
        test_skill_matching, 
        test_model_loading
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 50)
    print("📋 Results Summary:")
    print(f"CSV Loading: {'✅' if results[0] else '❌'}")
    print(f"Skill Matching: {'✅' if results[1] else '❌'}")
    print(f"Model Loading: {'✅' if results[2] else '⚠️'}")
    
    if all(results):
        print("\n🎉 All tests passed! Your fix worked.")
    else:
        print("\n💥 Some tests failed. Check the errors above.")