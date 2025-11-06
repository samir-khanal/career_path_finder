import sys
import os
from pathlib import Path

# Add the src directory to Python path
current_dir = Path(__file__).parent
root_dir = current_dir.parent  # Go up to root directory
src_dir = root_dir / "src"     # Then into src
sys.path.append(str(src_dir))

from parsing.enhanced_parser import enhanced_extract_sections

def extract_text_from_pdf(file_path):
    """Simple PDF text extraction"""
    try:
        import PyPDF2
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
    except ImportError:
        print("Installing PyPDF2...")
        os.system("pip install PyPDF2")
        import PyPDF2
        return extract_text_from_pdf(file_path)
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def test_simple():
    # FIXED PATH: Go up to root, then into demo_samples
    resume_path = root_dir / "demo_samples" / "Resume.pdf"
    
    if not os.path.exists(resume_path):
        print(f"❌ Resume file not found at: {resume_path}")
        print("Current working directory:", os.getcwd())
        print("\nLooking for files in demo_samples folder:")
        demo_samples_dir = root_dir / "demo_samples"
        if demo_samples_dir.exists():
            files = list(demo_samples_dir.iterdir())
            if files:
                for file in files:
                    print(f"  - {file.name}")
            else:
                print("  (folder is empty)")
        else:
            print("  demo_samples folder doesn't exist")
        return
    
    print(f"📄 Testing with: {resume_path}")
    
    # Extract text
    text = extract_text_from_pdf(str(resume_path))  # Convert to string for PyPDF2
    
    if not text:
        print("❌ Could not extract text from PDF")
        return
    
    print(f"✅ Extracted {len(text)} characters")
    
    # Parse the resume - CONVERT PATH TO STRING
    print("\n🔄 Parsing resume...")
    results = enhanced_extract_sections(text, str(resume_path))  # FIX: Convert to string
    
    # Display results
    print("\n" + "="*60)
    print("📊 PARSING RESULTS")
    print("="*60)
    
    print(f"\n🎯 SKILLS ({len(results['skills'])} found):")
    for i, skill in enumerate(results['skills'], 1):
        print(f"   {i}. {skill}")
    
    print(f"\n🎓 EDUCATION ({len(results['education'])} found):")
    for i, edu in enumerate(results['education'], 1):
        print(f"   {i}. {edu}")
    
    print(f"\n💼 EXPERIENCE ({len(results['experience'])} found):")
    for i, exp in enumerate(results['experience'], 1):
        preview = exp[:120] + "..." if len(exp) > 120 else exp
        print(f"   {i}. {preview}")
    
    print(f"\n📜 CERTIFICATIONS ({len(results['certifications'])} found):")
    for i, cert in enumerate(results['certifications'], 1):
        print(f"   {i}. {cert}")
    
    # Summary
    print("\n" + "="*60)
    print("📈 SUMMARY:")
    print(f"   Skills: {len(results['skills'])} items")
    print(f"   Education: {len(results['education'])} items") 
    print(f"   Experience: {len(results['experience'])} items")
    print(f"   Certifications: {len(results['certifications'])} items")
    print("="*60)

if __name__ == "__main__":
    test_simple()