# src/parsing/advanced_pdf_parser.py
import pdfplumber
from pdfminer.high_level import extract_text
from pathlib import Path
from typing import Optional
import tempfile
import os

try:
    from pdf2image import convert_from_path
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("⚠️ OCR dependencies not installed. Run: pip install pdf2image pytesseract pillow")

def extract_text_advanced(pdf_path: str, use_ocr: bool = True) -> Optional[str]:
    """
    Advanced PDF text extraction with OCR fallback
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    
    text = ""
    
    # Strategy 1: Try pdfplumber first (best for modern PDFs)
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        print(f"✅ pdfplumber extracted {len(text)} characters")
    except Exception as e:
        print(f"❌ pdfplumber failed: {e}")
    
    # Strategy 2: If little text, try pdfminer
    if len(text.strip()) < 100:
        try:
            pdfminer_text = extract_text(pdf_path)
            if pdfminer_text and len(pdfminer_text.strip()) > len(text.strip()):
                text = pdfminer_text
                print(f"✅ pdfminer extracted {len(text)} characters")
        except Exception as e:
            print(f"❌ pdfminer failed: {e}")
    
    # Strategy 3: If still little text and OCR available, use OCR
    if use_ocr and OCR_AVAILABLE and len(text.strip()) < 100:
        print("🔄 Trying OCR extraction...")
        ocr_text = extract_text_with_ocr(pdf_path)
        if ocr_text and len(ocr_text.strip()) > len(text.strip()):
            text = ocr_text
            print(f"✅ OCR extracted {len(text)} characters")
    
    return text if text.strip() else None

def extract_text_with_ocr(pdf_path: str) -> Optional[str]:
    """Extract text from PDF using OCR"""
    if not OCR_AVAILABLE:
        print("⚠️ OCR not available")
        return None
        
    try:
        # Convert PDF to images
        images = convert_from_path(pdf_path, dpi=300)
        
        text = ""
        for i, image in enumerate(images):
            # Use OCR on each page
            page_text = pytesseract.image_to_string(image)
            text += f"--- Page {i+1} ---\n{page_text}\n"
        
        return text
    except Exception as e:
        print(f"❌ OCR extraction failed: {e}")
        return None

def is_scanned_pdf(pdf_path: str) -> bool:
    """Check if PDF is likely scanned (image-based)"""
    try:
        # Extract text with regular methods
        text = extract_text_advanced(pdf_path, use_ocr=False)
        
        # If very little text extracted, it's likely scanned
        if text and len(text.strip()) < 100:
            return True
        return False
    except:
        return True