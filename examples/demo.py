import sys
import os
from pathlib import Path

# Add the project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.parsing import parse_resume

def show_parsing(file_path):
    print(f"\n=== Parsing: {file_path.name} ===")
    try:
        # parse_resume returns a DICTIONARY, not text!
        result = parse_resume(str(file_path))
        
        if result is None:
            print("❌ Failed to parse resume")
            return
            
        print("\n📋 Extracted Sections:")
        print(f"   Skills: {len(result.get('skills', []))} found")
        print(f"   Education: {len(result.get('education', []))} found")  
        print(f"   Experience: {len(result.get('experience', []))} found")
        
        print("\n🔍 Skills Found:")
        skills = result.get('skills', [])
        if skills:
            for i, skill in enumerate(skills[:5]):  # Show first 5 skills
                print(f"   {i+1}. {skill}")
            if len(skills) > 5:
                print(f"   ... and {len(skills) - 5} more")
        else:
            print("   No skills detected")
            
        print("\n🎓 Education:")
        for edu in result.get('education', [])[:3]:  # Show first 3 education entries
            print(f"   - {edu}")
            
        print("\n💼 Experience:")
        for exp in result.get('experience', [])[:3]:  # Show first 3 experience entries
            print(f"   - {exp}")

    except Exception as e:
        print(f"❌ Error parsing {file_path.name}: {str(e)}")
        import traceback
        traceback.print_exc()  # Show full error traceback

if __name__ == "__main__":
    samples_dir = Path("data/demo_samples")
    if not samples_dir.exists():
        samples_dir = Path("demo_samples")  # Fallback to old location
        
    samples = list(samples_dir.glob("*"))
    if not samples:
        print("No sample files found. Checked:")
        print(f"- {Path('data/demo_samples').absolute()}")
        print(f"- {Path('demo_samples').absolute()}")
    else:
        print(f"Found {len(samples)} sample files:")
        for resume in samples:
            show_parsing(resume)