# career_path_finder

## 📄 Resume Analyzer & Skill Matching

🚀 An intelligent Resume Analyzer that parses resumes (PDF/DOCX), extracts candidate information, and performs skill matching against predefined career paths (e.g., Data Scientist, Web Developer, etc.).
Built with Python, NLP, and Machine Learning, this tool helps recruiters, students, and career services quickly evaluate resumes and identify skill gaps.

## ✨ Features

📑 Resume Parsing – Extracts text, tables, and structured information from PDF/DOCX files.

🧹 Text Cleaning & Preprocessing – Removes noise, normalizes text for NLP processing.

🧠 ML-powered Resume Parser – Enhanced parser for better entity recognition (skills, education, experience).

🎯 Skill Matching – Matches extracted skills with career path requirements.

📊 Skill Gap Analysis – Identifies missing skills for a target job role.

🖥 Streamlit Web App – User-friendly interface to upload resumes and view analysis.

## 🛠 Tech Stack

### Programming Language: Python 3.x

### Libraries & Tools:

spacy, nltk – NLP processing

scikit-learn, joblib – ML models

pandas, numpy – Data handling

pdfminer, python-docx – Resume parsing

Streamlit – Web frontend

⚡️ **Installation & Setup**

### Clone the repository
```bash
git clone https://github.com/YOUR-USERNAME/career_path_finder.git  
```
### Create virtual environment & install dependencies
``` 
python -m venv venv
source .venv/bin/activate   # On Linux/Mac
.venv\Scripts\activate      # On Windows
pip install -r requirements.txt
```

### Run Streamlit App
```
cd app
streamlit run streamlit_app_enhanced.py
```

## 📊 Usage

Upload a resume (PDF/DOCX) via the Streamlit app.

Get extracted details: Name, Email, Education, Experience, Skills.

Select a career path to check skill matching & gaps

## 👤 Author
Samir Khanal
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue)](https://www.linkedin.com/in/samir-khanal7/)
