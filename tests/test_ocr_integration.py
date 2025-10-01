# tests/test_ocr_integration.py
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_ocr_integration():
    """Test that OCR integration works with current structure"""
    from src.parsing import parse_resume
    from src.parsing.pdf_parser import extract_text_from_pdf
    from src.parsing.advanced_pdf_parser import OCR_AVAILABLE
    
    print("🧪 Testing OCR Integration")
    print("=" * 50)
    
    print(f"OCR Available: {OCR_AVAILABLE}")
    
    # Test with different possible paths
    test_paths = [
        Path("demo_samples/Resume_Samir.pdf"),  # Relative to project root
        Path("app/demo_samples/professional.pdf"),  # Relative to project root
        Path("tests/test_data/pdfs/simple.pdf"),  # Test file we know exists
    ]
    
    test_pdf = None
    for path in test_paths:
        full_path = project_root / path
        if full_path.exists():
            test_pdf = full_path
            print(f"✅ Found test PDF: {path}")
            break
    
    if test_pdf:
        print(f"📄 Testing with: {test_pdf}")
        
        # Test direct PDF parsing
        text = extract_text_from_pdf(str(test_pdf))
        
        if text:
            print(f"✅ PDF parsing successful: {len(text)} characters")
            print(f"Text sample: {text[:200]}...")
            
            # Check if it's likely a scanned PDF
            if len(text.strip()) < 100:
                print("⚠️ Very little text extracted - might be scanned PDF")
            else:
                print("✅ Good amount of text extracted")
        else:
            print("❌ PDF parsing failed - no text extracted")
        
        # Test full resume parsing
        result = parse_resume(str(test_pdf))
        if result:
            print(f"✅ Resume parsing successful")
            print(f"Skills found: {result.get('skills', [])}")
            print(f"Skills count: {len(result.get('skills', []))}")
            
            if "error" in result:
                print(f"Error: {result['error']}")
        else:
            print("❌ Resume parsing failed")
            
    else:
        print("⚠️ No test PDF found in common locations")
        print("Please upload a PDF through Streamlit first or run create_test_files.py")

if __name__ == "__main__":
    test_ocr_integration()