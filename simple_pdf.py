# create simple_pdf.py
from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

pdf.cell(200, 10, txt="John Doe - Data Scientist", ln=1, align='C')
pdf.ln(10)

pdf.cell(200, 10, txt="SKILLS:", ln=1)
pdf.multi_cell(0, 10, txt="Python, Machine Learning, SQL, Data Visualization, Statistics, Deep Learning")
pdf.ln(5)

pdf.cell(200, 10, txt="EDUCATION:", ln=1)
pdf.multi_cell(0, 10, txt="MS in Computer Science - Tech University (2022-2024)")
pdf.ln(5)

pdf.cell(200, 10, txt="EXPERIENCE:", ln=1)
pdf.multi_cell(0, 10, txt="Data Scientist at AI Company (2024-Present)\n- Developed ML models\n- Analyzed big data")

output_path = "tests/test_data/pdfs/simple.pdf"
pdf.output(output_path)