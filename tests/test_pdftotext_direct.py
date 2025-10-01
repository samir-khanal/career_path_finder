# tests/test_pdftotext_direct.py
import sys
from pathlib import Path
import subprocess
import tempfile
import os

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_pdftotext_direct():
    """Test pdftotext command directly without any Python wrappers"""
    print("🧪 Testing Direct pdftotext Command")
    print("=" * 50)
    
    # Use the poppler path that we know works
    poppler_path = r"C:\poppler\Library\bin"
    pdftotext_exe = os.path.join(poppler_path, "pdftotext.exe")
    
    test_pdf = Path("demo_samples/Resume_Samir.pdf")
    
    if test_pdf.exists():
        print(f"📄 Testing with: {test_pdf}")
        print(f"📊 File size: {test_pdf.stat().st_size} bytes")
        
        if os.path.exists(pdftotext_exe):
            print(f"✅ pdftotext.exe found")
            
            # Create temporary output file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
                temp_path = temp_file.name
            
            try:
                print("🔄 Running pdftotext command...")
                
                # Build command with various options
                cmd = [
                    pdftotext_exe,
                    "-layout",      # Maintain layout
                    "-enc", "UTF-8", # UTF-8 encoding  
                    "-eol", "unix",  # Unix line endings
                    "-nopgbrk",     # No page breaks
                    str(test_pdf),
                    temp_path
                ]
                
                print(f"🔧 Command: {' '.join(cmd)}")
                
                # Run the command
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                print(f"📊 Return code: {result.returncode}")
                
                if result.returncode == 0:
                    if os.path.exists(temp_path):
                        file_size = os.path.getsize(temp_path)
                        print(f"📊 Output file created: {file_size} bytes")
                        
                        if file_size > 0:
                            # Read the extracted text
                            with open(temp_path, 'r', encoding='utf-8', errors='ignore') as f:
                                text = f.read()
                            
                            print(f"✅ SUCCESS! Extracted {len(text)} characters")
                            print(f"📝 First 500 characters:")
                            print("-" * 50)
                            print(text[:500])
                            print("-" * 50)
                            
                            # Save to a file for inspection
                            output_file = project_root / "extracted_text.txt"
                            with open(output_file, 'w', encoding='utf-8') as f:
                                f.write(text)
                            print(f"💾 Full text saved to: {output_file}")
                            
                            return text
                        else:
                            print("❌ Output file is empty (0 bytes)")
                    else:
                        print("❌ Output file was not created")
                else:
                    print("❌ pdftotext command failed")
                    if result.stderr:
                        print(f"📤 stderr: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                print("❌ Command timed out after 30 seconds")
            except Exception as e:
                print(f"❌ Error: {e}")
            finally:
                # Clean up
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
        else:
            print(f"❌ pdftotext.exe not found at: {pdftotext_exe}")
    else:
        print("⚠️ Test PDF not found")
        # List available PDFs
        demo_dir = project_root / "demo_samples"
        if demo_dir.exists():
            pdf_files = list(demo_dir.glob("*.pdf"))
            if pdf_files:
                print("Available PDFs:")
                for pdf in pdf_files:
                    print(f"   - {pdf.name}")

if __name__ == "__main__":
    test_pdftotext_direct()