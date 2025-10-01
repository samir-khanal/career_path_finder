# src/parsing/pdf_parser_final.py
import subprocess
import os
import tempfile
from pathlib import Path
from typing import Optional

try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image
    OCR_AVAILABLE = True
    
    # Auto-detect Tesseract path
    def find_tesseract_path():
        possible_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            os.path.expanduser(r"~\AppData\Local\Tesseract-OCR\tesseract.exe")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Try to find in PATH
        try:
            subprocess.run(['tesseract', '--version'], capture_output=True, check=True)
            return 'tesseract'  # Use from PATH
        except:
            return None
    
    tesseract_path = find_tesseract_path()
    if tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        print(f"✅ Tesseract configured: {tesseract_path}")
    else:
        print("❌ Tesseract not found. Please install from: https://github.com/UB-Mannheim/tesseract/wiki")
        OCR_AVAILABLE = False
        
except ImportError as e:
    print(f"❌ OCR dependencies missing: {e}")
    OCR_AVAILABLE = False

class FinalPDFExtractor:
    def __init__(self):
        self.poppler_path = r"C:\poppler\Library\bin"
        self.pdftotext_exe = os.path.join(self.poppler_path, "pdftotext.exe")
        
    def extract_text(self, pdf_path: str) -> Optional[str]:
        """Extract text with OCR fallback for scanned PDFs"""
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        print(f"🔍 Extracting from: {path.name}")
        print(f"📊 File size: {path.stat().st_size} bytes")
        
        # Method 1: Try pdftotext first (for text-based PDFs)
        text = self._extract_with_pdftotext(pdf_path)
        if text and text.strip():
            print(f"✅ Text-based PDF: {len(text)} characters")
            return text
        
        # Method 2: If pdftotext fails, use OCR (for scanned PDFs)
        if OCR_AVAILABLE:
            print("🔄 Text extraction failed, trying OCR...")
            ocr_text = self._extract_with_ocr(pdf_path)
            if ocr_text and ocr_text.strip():
                print(f"✅ OCR extracted: {len(ocr_text)} characters")
                return ocr_text
        else:
            print("❌ OCR not available - install Tesseract and dependencies")
        
        print("❌ All extraction methods failed")
        return None
    
    def _extract_with_pdftotext(self, pdf_path: str) -> Optional[str]:
        """Extract from text-based PDFs"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
                temp_path = temp_file.name
            
            cmd = [self.pdftotext_exe, "-layout", "-enc", "UTF-8", str(pdf_path), temp_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and os.path.exists(temp_path):
                with open(temp_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
                
                # Clean up
                os.unlink(temp_path)
                
                return text
                
        except Exception as e:
            print(f"⚠️ pdftotext failed: {e}")
        
        return None
    
    def _extract_with_ocr(self, pdf_path: str) -> Optional[str]:
        """Extract text from scanned PDFs using OCR"""
        try:
            print("📄 Converting PDF to images for OCR...")
            
            # Convert PDF to images
            images = convert_from_path(
                pdf_path,
                dpi=200,  # Balanced resolution for speed/quality
                poppler_path=self.poppler_path
            )
            
            text = ""
            total_pages = len(images)
            
            for i, image in enumerate(images):
                print(f"🔍 OCR processing page {i+1}/{total_pages}...")
                
                # Use OCR on the image
                page_text = pytesseract.image_to_string(
                    image,
                    config='--psm 6'  # Uniform block of text
                )
                
                if page_text.strip():
                    text += f"--- Page {i+1} ---\n{page_text}\n"
                else:
                    print(f"   ⚠️ Page {i+1}: No text detected by OCR")
            
            return text if text.strip() else None
            
        except Exception as e:
            print(f"❌ OCR extraction failed: {e}")
            return None

# Global instance
pdf_extractor = FinalPDFExtractor()

def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
    """Main extraction function"""
    return pdf_extractor.extract_text(pdf_path)