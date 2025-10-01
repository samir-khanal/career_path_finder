import re
from typing import Dict, List
from .text_cleaner import clean_skill_list
from .pdf_table_extractor import extract_skills_from_pdf_tables

def enhanced_extract_sections(text: str, file_path: str = None) -> Dict[str, List[str]]:
    """
    Enhanced section extraction that works for ALL resume types
    """
    sections = {
        "skills": [],
        "education": [],
        "experience": [],
        "certifications": []
    }
    
    # STRATEGY 1: Direct table extraction for PDFs
    table_skills = []
    if file_path and file_path.lower().endswith('.pdf'):
        try:
            table_skills = extract_skills_from_pdf_tables(file_path)
            sections["skills"].extend(table_skills)
            print(f"DEBUG: Table extraction found {len(table_skills)} skills")
        except Exception as e:
            print(f"Table extraction failed: {e}")
    
    # STRATEGY 2: Regex section parsing
    section_patterns = {
        "skills": r"(?:skills|technical skills|technologies|expertise|competencies)[:\-]?\s*(.*?)(?=education|experience|work|projects|$|certifications)",
        "education": r"(?:education|academic background|qualifications)[:\-]?\s*(.*?)(?=experience|skills|work|projects|$|certifications)", 
        "experience": r"(?:experience|work history|employment|professional)[:\-]?\s*(.*?)(?=education|skills|projects|certifications|$)",
        "certifications": r"(?:certifications|certificate|qualifications)[:\-]?\s*(.*?)(?=education|experience|skills|$)"
    }
    
    text_lower = text.lower()
    
    for section, pattern in section_patterns.items():
        match = re.search(pattern, text_lower, re.IGNORECASE | re.DOTALL)
        if match:
            content = match.group(1).strip()
            
            if section == "skills":
                items = split_skills_string(content)
            else:
                items = [item.strip() for item in re.split(r'[\n•\-]', content) if item.strip()]
            
            sections[section].extend(items)
    
    # STRATEGY 3: Extract skills from entire text using keyword scanning
    if len(sections["skills"]) < 5:  # If few skills found
        text_skills = extract_skills_from_text_keywords(text)
        sections["skills"].extend(text_skills)
        print(f"DEBUG: Keyword extraction found {len(text_skills)} skills")
    
    # Clean and deduplicate skills
    if sections["skills"]:
        sections["skills"] = clean_skill_list(sections["skills"])
        print(f"🎯 Final skills after cleaning: {len(sections['skills'])} skills")
    
    return sections 

def extract_skills_from_text_keywords(text: str) -> List[str]:
    """Extract skills by scanning entire text for keywords"""
    skills_found = set()
    
    # Common technical skills
    technical_skills = [
        # Programming Languages
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby', 'go', 'swift', 'kotlin',
        'r', 'scala', 'rust', 'matlab', 'perl', 'bash', 'shell', 'powershell',
        
        # Data Science & ML
        'machine learning', 'deep learning', 'artificial intelligence', 'ai', 'data science', 'data analysis',
        'data visualization', 'statistical analysis', 'predictive modeling', 'regression', 'classification',
        'clustering', 'natural language processing', 'nlp', 'computer vision', 'neural networks', 'time series',
        'a/b testing', 'hypothesis testing', 'exploratory data analysis', 'eda', 'feature engineering',
        'model selection', 'cross validation', 'hyperparameter tuning', 'ensemble methods',
        # Data Tools
        'pandas', 'numpy', 'scipy', 'scikit-learn', 'sklearn', 'tensorflow', 'pytorch', 'keras', 'mxnet',
        'matplotlib', 'seaborn', 'plotly', 'bokeh', 'd3.js', 'ggplot2', 'tableau', 'power bi', 'powerbi',
        'qlik', 'looker', 'jupyter', 'google colab', 'rstudio', 'spss', 'sas', 'stata',
        
        # Databases
        'sql', 'mysql', 'postgresql', 'postgres', 'oracle', 'sql server', 'mongodb', 'redis', 'couchbase',
        'dynamodb', 'cassandra', 'neo4j', 'sqlite', 'firebase', 'cosmos db', 'bigquery', 'snowflake',
        
        # Big Data
        'spark', 'pyspark', 'hadoop', 'hive', 'kafka', 'storm', 'flink', 'beam', 'airflow', 'luigi',
        'presto', 'hbase', 'cassandra', 'elasticsearch', 'splunk',
        # Cloud & DevOps
        'aws', 'amazon web services', 'azure', 'microsoft azure', 'gcp', 'google cloud', 'docker', 'kubernetes',
        'jenkins', 'git', 'github', 'gitlab', 'bitbucket', 'terraform', 'ansible', 'puppet', 'chef',
        'ci/cd', 'continuous integration', 'continuous deployment', 'devops', 'mlops',
        
        # Web Development
        'html', 'css', 'react', 'angular', 'vue', 'node', 'node.js', 'express', 'django', 'flask', 'spring',
        'laravel', 'ruby on rails', 'asp.net', 'php', 'wordpress', 'drupal', 'joomla',
        
        # Mobile Development
        'android', 'ios', 'swift', 'react native', 'flutter', 'xamarin', 'ionic', 'cordova',
        
        # Tools & Software
        'excel', 'powerpoint', 'word', 'outlook', 'sharepoint', 'jira', 'confluence', 'slack', 'teams',
        'zoom', 'photoshop', 'illustrator', 'figma', 'sketch', 'invision',
        'adobe xd', 'canva', 'notion', 'evernote',
        # Methodologies
        'agile', 'scrum', 'kanban', 'waterfall', 'lean', 'six sigma', 'devops',
        
        # Soft Skills
        'communication', 'problem solving', 'teamwork', 'leadership', 'project management', 'time management',
        'critical thinking', 'analytical skills', 'creativity', 'adaptability', 'presentation', 'negotiation'
    ]
    
    text_lower = text.lower()
    
    for skill in technical_skills:
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            skills_found.add(skill)
    
    return list(skills_found)

# KEEP YOUR EXISTING helper functions
def split_skills_string(skills_text: str) -> List[str]:
    if not skills_text:
        return []
    
    skills = []
    
    # Remove common section headers
    skills_text = re.sub(r'^(?:skills?|technologies?|tools?|frameworks?|languages?)[:\-]\s*', '', skills_text, flags=re.IGNORECASE)
    
    # Try different splitting strategies
    delimiters = [',', ';', '•', '\n', '/', '|', '&']
    
    for delimiter in delimiters:
        if delimiter in skills_text:
            parts = skills_text.split(delimiter)
            for part in parts:
                skill = part.strip()
                if skill and len(skill) > 1 and not skill.isdigit():
                    # Clean up the skill
                    skill = re.sub(r'^\W+|\W+$', '', skill)  # Remove surrounding punctuation
                    if skill:
                        skills.append(skill)
            break
    else:
        # If no delimiters found, try to split by common patterns
        # Handle "Swift Objective-C Python" pattern
        skills = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*|[A-Z]+', skills_text)
        skills = [skill.strip() for skill in skills if skill.strip() and len(skill) > 1]
    
    return skills

def split_skills_by_uppercase(text: str) -> List[str]:
    skills = re.findall(r'[A-Z][a-z]+|[A-Z]+(?=[A-Z]|$)', text)
    return [skill.strip() for skill in skills if skill.strip()]