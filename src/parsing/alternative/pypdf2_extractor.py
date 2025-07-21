# Provides a fallback parser if the primary PDF parser (pdfminer) fails.
# Different PDF libraries handle edge cases differently (e.g., scanned text, tables).
import PyPDF2
from typing import Optional
from pathlib import Path

class PDFExtractor:
    """PyPDF2-based extractor with better error handling"""
    
    def extract_text(self, pdf_path: str) -> Optional[str]:
        try:
            text = []
            with Path(pdf_path).open('rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    if (page_text := page.extract_text()):
                        text.append(page_text)
            return '\n'.join(text) if text else None
        except Exception as e:
            print(f"PyPDF2 extraction failed: {e}")
            return None