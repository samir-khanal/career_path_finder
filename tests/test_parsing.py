'''from src.parsing import parse_resume

for pdf in ["text_only.pdf", "with_tables.pdf"]:
    print(f"=== {pdf} ===")
    print(parse_resume(f"test_pdfs/{pdf}")[:500])'''  # First 500 chars
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from pathlib import Path
from src.parsing import parse_resume

# Test files
PDF_SIMPLE = Path("tests/test_data/pdfs/simple.pdf")
PDF_TABLES = Path("tests/test_data/pdfs/tables.pdf")
DOCX_SIMPLE = Path("tests/test_data/docs/simple.docx")
DOCX_TABLES = Path("tests/test_data/docs/tables.docx")

def test_pdf_parsing():
    """Test basic PDF parsing - now returns DICT not text"""
    data = parse_resume(str(PDF_SIMPLE))
    assert data, "Failed to extract resume"
    assert isinstance(data, dict), "Should return dictionary"
    # Check if we extracted any structured data
    assert any([data.get("skills"), data.get("education"), data.get("experience")])

def test_pdf_tables():
    """Test PDF with tables - check if any content is extracted"""
    data = parse_resume(str(PDF_TABLES))
    assert data, "Failed to extract table content"
    # Check if any meaningful data was extracted
    assert any([data.get("skills"), data.get("education"), data.get("experience")])

def test_docx_parsing():
    """Test basic DOCX parsing - returns structured dict"""
    data = parse_resume(str(DOCX_SIMPLE))
    assert data, "Failed to extract DOCX"
    assert isinstance(data, dict), "Should return dictionary"
    assert any([data.get("skills"), data.get("education"), data.get("experience")])

def test_docx_tables():
    """Test DOCX with skill tables - check if any skills are detected"""
    data = parse_resume(str(DOCX_TABLES))
    assert data, "Failed to extract DOCX with tables"
    # Check if we got any skills or content
    assert any([data.get("skills"), data.get("education"), data.get("experience")])

def test_error_handling():
    """Test invalid files"""
    with pytest.raises(ValueError):
        parse_resume("invalid_file.txt")


if __name__ == "__main__":
    # Run all tests manually
    print("🚀 Running Resume Parser Tests...")
    print("=" * 50)
    
    tests = [
        test_pdf_parsing,
        test_pdf_tables, 
        test_docx_parsing,
        test_docx_tables,
        test_error_handling
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            print(f"✅ {test_func.__name__} - PASSED")
            passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__} - FAILED: {e}")
            failed += 1
    
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed > 0:
        exit(1)  # Exit with error code if any tests failed