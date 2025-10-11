 # Main interface for the parsing module
#NOTES:
# Path: Helps work with file paths across Windows/Mac/Linux
# Optional: Says a function might return None
# Literal: Restricts input choices (like only allowing "auto", "pypdf2", or "pdfminer")

''' def parse_pdf(pdf_path, engine="auto"):
    """
    Parses PDF files using either:
    - "pypdf2" (faster for small files)
    - "pdfminer" (more reliable)
    - "auto" (chooses automatically)
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")'''

from pathlib import Path
from typing import Optional, Dict, List, Literal
from .pdf_parser_improved import extract_text_from_pdf
from .docx_parser import extract_text_from_docx
from .text_cleaner import clean_extracted_text
from .enhanced_parser import enhanced_extract_sections as extract_sections

__version__ = "1.0.0"
__all__ = ['parse_resume', 'parse_pdf']  # Public API
# __all__ - it tells (other Python files) what (functions) they can use

# -> Optional[str]: Might return text (str) or None if failed
def parse_pdf(pdf_path: str, engine: Literal["auto", "pypdf2", "pdfminer"] = "auto") -> Optional[str]:
    """Cross-platform PDF parser with multiple fallback strategies"""
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    text = extract_text_from_pdf(pdf_path)
    return clean_extracted_text(text) if text else None

def parse_resume(file_path: str) -> Optional[Dict[str, List[str]]]:
    """Unified parser that returns structured data"""
    path = Path(file_path)
    suffix = path.suffix.lower()
    
    # Extract raw text first
    raw_text = None
    if suffix == '.pdf':
        raw_text = parse_pdf(file_path, engine="auto")
    elif suffix == '.docx':
        raw_text = extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format: {suffix}")

    if not raw_text:
        return None

    # Convert raw text to structured data
    return extract_sections(raw_text, file_path)  # This should return dict