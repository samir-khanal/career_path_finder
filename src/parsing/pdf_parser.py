from pdfminer.high_level import extract_text
from pathlib import Path
from typing import Optional

def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
    """
    Extract text from PDF using pdfminer.six
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extracted text or None if extraction fails
    """
    try:
        if not Path(pdf_path).exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Extract and clean basic text
        text = extract_text(pdf_path)
        return text if text.strip() else None
        
    except Exception as e:
        print(f"[pdfminer] Extraction error: {e}")
        return None
    
# Add to src/parsing/pdf_table_extractor.py
'''import pdfplumber  # Better for table detection

def extract_pdf_tables(pdf_path):
    """Extract structured tables from PDF"""
    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables.extend(page.extract_tables())
    return tables

# Modified pdf_parser.py
def extract_text_from_pdf(pdf_path):
    text = extract_text(pdf_path)  # Basic text
    tables = extract_pdf_tables(pdf_path)  # Structured tables
    table_text = "\n".join([cell for table in tables for row in table for cell in row])
    return f"{text}\n{table_text}" '''