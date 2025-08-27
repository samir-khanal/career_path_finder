# test_skill_matching.py
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

def test_skill_normalization():
    """Test if skill normalization works correctly"""
    try:
        from src.parsing.ml.skill_matcher import normalize_skill_to_base, debug_normalization_examples
        
        print("🧪 Testing Skill Normalization")
        print("=" * 50)
        
        # Test normalization examples
        debug_normalization_examples()
        
        # Test specific cases that should work
        test_cases = [
            ("Python", "python"),
            ("ML", "machine learning"),
            ("Sql", "sql"),
            ("Data Visualization", "data visualization"),
            ("Pandas", "pandas"),
            ("React.js", "react")
        ]
        
        print("\n🔍 Testing specific skill conversions:")
        for input_skill, expected_output in test_cases:
            result = normalize_skill_to_base(input_skill)
            status = "✅" if result == expected_output else "❌"
            print(f"{status} '{input_skill}' -> '{result}' (expected: '{expected_output}')")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_matching_with_real_data():
    """Test matching with actual resume skills"""
    try:
        from src.parsing.ml.skill_matcher import compute_skill_gap, debug_skill_matching
        
        print("\n🧪 Testing Skill Matching with Real Data")
        print("=" * 50)
        
        # Your actual resume skills
        resume_skills = ["Python", "Machine Learning", "Sql", "Data Visualization", "Statistics", "Deep Learning"]
        
        # Required skills for a role
        required_skills = ["python", "machine learning", "sql", "data visualization", "tableau", "advanced sql"]
        
        print("Resume skills:", resume_skills)
        print("Required skills:", required_skills)
        print()
        
        # Debug the matching process
        debug_skill_matching(resume_skills, required_skills)
        
        # Test actual matching
        result = compute_skill_gap(resume_skills, required_skills)
        
        print("✅ Matched:", result["matched"])
        print("❌ Missing:", result["missing"])
        
        # Calculate score
        total = len(required_skills)
        matched = len(result["matched"])
        score = (matched / total) * 100 if total > 0 else 0
        
        print(f"📊 Score: {score:.1f}% ({matched}/{total} skills matched)")
        
        # Should match at least Python, ML, SQL, and Data Visualization
        expected_min_matches = 4
        if matched >= expected_min_matches:
            print("🎉 Skill matching is WORKING!")
        else:
            print(f"💥 Expected at least {expected_min_matches} matches, got {matched}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_skill_normalization()
    test_matching_with_real_data()