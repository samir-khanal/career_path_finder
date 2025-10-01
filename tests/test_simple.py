# tests/test_simple.py
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.parsing.ml.skill_matcher import analyze_resume
from src.parsing import parse_resume

def test_with_created_files():
    """Test with the files created by create_test_files.py"""
    print("🧪 Testing resume analyzer with created test files...")
    
    # Test with simple PDF
    simple_pdf = Path("tests/test_data/pdfs/simple.pdf")
    if simple_pdf.exists():
        print(f"📄 Testing with: {simple_pdf}")
        try:
            result = analyze_resume(str(simple_pdf))
            skills = result["parsed"].get("skills", [])
            print(f"✅ Analysis completed!")
            print(f"   Skills found: {skills}")
            print(f"   Skills count: {len(skills)}")
            print(f"   Match score: {result.get('match_score', 0)}%")
            
            # Test basic parsing separately
            parsed_data = parse_resume(str(simple_pdf))
            print(f"   Direct parse skills: {parsed_data.get('skills', [])}")
            
        except Exception as e:
            print(f"❌ Error analyzing {simple_pdf}: {e}")
    else:
        print("⚠️ Simple PDF not found. Run create_test_files.py first")
    
    print("\n" + "="*50 + "\n")
    
    # Test with table PDF
    table_pdf = Path("tests/test_data/pdfs/tables.pdf")
    if table_pdf.exists():
        print(f"📊 Testing with: {table_pdf}")
        try:
            result = analyze_resume(str(table_pdf))
            skills = result["parsed"].get("skills", [])
            print(f"✅ Analysis completed!")
            print(f"   Skills found: {skills}")
            print(f"   Skills count: {len(skills)}")
            print(f"   Match score: {result.get('match_score', 0)}%")
            
        except Exception as e:
            print(f"❌ Error analyzing {table_pdf}: {e}")
    else:
        print("⚠️ Table PDF not found. Run create_test_files.py first")

def test_skill_extraction():
    """Test skill extraction specifically"""
    print("\n🔍 Testing skill extraction...")
    
    # Create a simple test text with known skills
    test_text = """
    John Doe - Data Scientist
    SKILLS: Python, SQL, Machine Learning, Pandas, Data Visualization
    EXPERIENCE: Built ML models using Scikit-learn and TensorFlow
    EDUCATION: BS Computer Science
    """
    
    # Test the enhanced parser directly
    from src.parsing.enhanced_parser import enhanced_extract_sections
    sections = enhanced_extract_sections(test_text)
    
    print(f"✅ Skill extraction test:")
    print(f"   Found skills: {sections.get('skills', [])}")
    print(f"   Education: {sections.get('education', [])}")
    print(f"   Experience: {sections.get('experience', [])}")

def test_skill_matching():
    """Test the skill matching logic"""
    print("\n🎯 Testing skill matching...")
    
    from src.parsing.ml.skill_matcher import compute_skill_gap, normalize_skill_to_base
    
    # Test data
    resume_skills = ["python", "pandas", "sql", "machine learning"]
    required_skills = ["Python", "Pandas", "Numpy", "Data Visualization", "SQL"]
    
    result = compute_skill_gap(resume_skills, required_skills)
    
    print(f"✅ Skill matching test:")
    print(f"   Resume skills: {resume_skills}")
    print(f"   Required skills: {required_skills}")
    print(f"   Matched: {result.get('matched', [])}")
    print(f"   Missing: {result.get('missing', [])}")
    
    # Test normalization
    test_skills = ["Python", "PYTHON", "python", "Sql", "SQL", "scikit-learn", "sklearn"]
    normalized = [normalize_skill_to_base(skill) for skill in test_skills]
    print(f"   Normalization test: {list(zip(test_skills, normalized))}")

if __name__ == "__main__":
    print("🚀 Starting Comprehensive Resume Analyzer Tests")
    print("=" * 60)
    
    test_with_created_files()
    test_skill_extraction() 
    test_skill_matching()
    
    print("=" * 60)
    print("🎉 All tests completed!")