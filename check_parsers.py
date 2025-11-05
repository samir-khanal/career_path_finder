# check_parsers.py
from pathlib import Path
import sys

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("🔍 Checking available parser files...")

parsing_dir = Path("src/parsing")
if parsing_dir.exists():
    print(f"\n📁 Files in {parsing_dir}:")
    for file in parsing_dir.glob("*.py"):
        print(f"  • {file.name}")
        
    # Try to import each parser
    print(f"\n🔄 Testing imports...")
    parsers_to_try = [
        'docx_parser', 
        'pdf_parser', 
        'advanced_pdf_parser',
        'resume_parser'
    ]
    
    for parser_name in parsers_to_try:
        try:
            module = __import__(f'src.parsing.{parser_name}', fromlist=[''])
            print(f"  ✅ {parser_name}: Success")
            # Check what classes/functions are available
            if hasattr(module, '__all__'):
                print(f"     Exports: {module.__all__}")
            else:
                # List public classes/functions
                items = [name for name in dir(module) if not name.startswith('_')]
                print(f"     Contents: {items[:5]}...")  # Show first 5
        except ImportError as e:
            print(f"  ❌ {parser_name}: {e}")

else:
    print(f"❌ Directory not found: {parsing_dir}")