'''from src.parsing import parse_resume

for pdf in ["text_only.pdf", "with_tables.pdf"]:
    print(f"=== {pdf} ===")
    print(parse_resume(f"test_pdfs/{pdf}")[:500])'''  # First 500 chars

import pytest
from pathlib import Path
from src.parsing import parse_resume

# Test files
PDF_SIMPLE = Path("tests/test_data/pdfs/simple.pdf")
PDF_TABLES = Path("tests/test_data/pdfs/tables.pdf")
DOCX_SIMPLE = Path("tests/test_data/docs/simple.docx")
DOCX_TABLES = Path("tests/test_data/docs/tables.docx")

def test_pdf_parsing():
    """Test basic PDF parsing"""
    text = parse_resume(str(PDF_SIMPLE))
    assert text, "Failed to extract text"
    assert "Experience" in text or "Skills" in text

def test_pdf_tables():
    """Test PDF with tables"""
    text = parse_resume(str(PDF_TABLES))
    assert "Education" in text, "Table content missing"

def test_docx_parsing():
    """Test basic DOCX parsing"""
    text = parse_resume(str(DOCX_SIMPLE))
    assert "Contact" in text, "Basic info missing"

def test_docx_tables():
    """Test DOCX with skill tables"""
    text = parse_resume(str(DOCX_TABLES))
    assert "Python" in text and "JavaScript" in text

def test_error_handling():
    """Test invalid files"""
    with pytest.raises(ValueError):
        parse_resume("invalid_file.txt")