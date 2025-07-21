# This  code is for Showing demo to our Supervisor not used for actual project development
from src.parsing import parse_resume
from pathlib import Path

def show_parsing(file_path):
    print(f"\n=== Parsing: {file_path.name} ===")
    try:

        text = parse_resume(str(file_path))
        
        print("\nExtracted Text Preview:")
        print(text[:300] + "...")  # Show first 300 characters
        
        print("\nKey Sections Found:")
        print(f"- Skills: {'Skills' in text}")
        print(f"- Experience: {'Experience' in text}")
        print(f"- Education: {'Education' in text}")

    except Exception as e:
        print(f"❌ Error parsing {file_path.name}: {str(e)}")
if __name__ == "__main__":
    samples = list(Path("demo_samples").glob("*"))
    if not samples:
        print("No sample files found in demo_samples directory.")
    else:
        for resume in samples:
            show_parsing(resume)