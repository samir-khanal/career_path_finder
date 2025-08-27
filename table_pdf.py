# table_pdf.py
from fpdf import FPDF
from pathlib import Path

# Create PDF with proper tables
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

# Personal Info
pdf.cell(200, 10, txt="JOHN SMITH - SENIOR DATA SCIENTIST", ln=1, align='C')
pdf.cell(200, 10, txt="john.smith@email.com | (555) 987-6543 | linkedin.com/in/johnsmith", ln=1, align='C')
pdf.ln(15)

# TECHNICAL SKILLS TABLE
pdf.set_font("Arial", 'B', 14)
pdf.cell(200, 10, txt="TECHNICAL SKILLS", ln=1)
pdf.set_font("Arial", size=11)

# Skills Table 1: Programming Languages
pdf.cell(200, 8, txt="Programming Languages:", ln=1)
data = [
    ["Language", "Years", "Proficiency"],
    ["Python", "5", "Expert"],
    ["SQL", "4", "Advanced"],
    ["R", "3", "Intermediate"],
    ["Java", "2", "Intermediate"]
]

col_width = 40
row_height = 8

for row in data:
    for item in row:
        pdf.cell(col_width, row_height, txt=str(item), border=1)
    pdf.ln(row_height)

pdf.ln(5)

# Skills Table 2: Data Science Tools
pdf.cell(200, 8, txt="Data Science Tools:", ln=1)
data2 = [
    ["Tool", "Category", "Proficiency"],
    ["TensorFlow", "ML Framework", "Expert"],
    ["Tableau", "Visualization", "Advanced"],
    ["Scikit-learn", "ML Library", "Expert"],
    ["PyTorch", "Deep Learning", "Intermediate"]
]

for row in data2:
    for item in row:
        pdf.cell(col_width, row_height, txt=str(item), border=1)
    pdf.ln(row_height)

pdf.ln(15)

# EDUCATION TABLE
pdf.set_font("Arial", 'B', 14)
pdf.cell(200, 10, txt="EDUCATION", ln=1)
pdf.set_font("Arial", size=11)

edu_data = [
    ["Degree", "Institution", "Year", "GPA"],
    ["PhD Data Science", "Tech University", "2022-2024", "3.9/4.0"],
    ["MS Computer Science", "State University", "2018-2020", "3.8/4.0"],
    ["BS Mathematics", "City College", "2014-2018", "3.7/4.0"]
]

col_widths = [50, 50, 30, 20]

for row in edu_data:
    for i, item in enumerate(row):
        pdf.cell(col_widths[i], 8, txt=str(item), border=1)
    pdf.ln(8)

pdf.ln(15)

# EXPERIENCE TABLE
pdf.set_font("Arial", 'B', 14)
pdf.cell(200, 10, txt="PROFESSIONAL EXPERIENCE", ln=1)
pdf.set_font("Arial", size=11)

exp_data = [
    ["Position", "Company", "Duration", "Technologies"],
    ["Senior Data Scientist", "AI Innovations", "2022-Present", "Python, TensorFlow, AWS"],
    ["Data Scientist", "Tech Solutions", "2020-2022", "SQL, Tableau, Scikit-learn"],
    ["Data Analyst", "DataWorks Inc", "2018-2020", "Python, Excel, SQL"]
]

col_widths_exp = [50, 40, 30, 60]

for row in exp_data:
    for i, item in enumerate(row):
        pdf.cell(col_widths_exp[i], 8, txt=str(item), border=1)
    pdf.ln(8)

# Save to file
output_path = Path("tests/test_data/pdfs/tables.pdf")
output_path.parent.mkdir(parents=True, exist_ok=True)
pdf.output(str(output_path))

print(f"✅ PDF with proper tables created: {output_path}")
print("📊 Contains: Skills Tables, Education Table, Experience Table")