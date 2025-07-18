 # Main interface for the parsing module
from pathlib import Path
from typing import Optional, Literal
from .pdf_parser import extract_text_from_pdf as pdfminer_extract
from .docx_parser import extract_text_from_docx
from .alternative.pypdf2_extractor import PDFExtractor
from .text_cleaner import clean_extracted_text

__version__ = "1.0.0"
__all__ = ['parse_resume', 'parse_pdf']  # Public API

def parse_pdf(
    pdf_path: str,
    engine: Literal["auto", "pypdf2", "pdfminer"] = "auto"
) -> Optional[str]:
    """Hybrid PDF parser with automatic fallback"""
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    
    # Try PyPDF2 first for small files (<5MB)
    if engine == "pypdf2" or (engine == "auto" and path.stat().st_size < 5_000_000):
        if (text := PDFExtractor().extract_text(pdf_path)):
            return clean_extracted_text(text)
        if engine == "pypdf2":  # Only fallback if in auto mode
            return None
    
    # Fallback to pdfminer
    return clean_extracted_text(pdfminer_extract(pdf_path))

def parse_resume(file_path: str) -> Optional[str]:
    """Unified parser for all supported formats"""
    path = Path(file_path)
    suffix = path.suffix.lower()
    
    if suffix == '.pdf':
        return parse_pdf(file_path, engine="auto")
    elif suffix == '.docx':
        if (text := extract_text_from_docx(file_path)):
            return clean_extracted_text(text)
    raise ValueError(f"Unsupported file format: {suffix}")