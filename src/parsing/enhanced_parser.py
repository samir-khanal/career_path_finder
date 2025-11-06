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
    
    # STRATEGY 2: Use your PROVEN regex patterns (they work!)
    section_patterns = {
        "skills": [
            r"(?i)(?:skills?/core\s+competencies|skills?|technical\s+skills?|technologies|expertise|competencies|core\s+competencies|proficiencies)[:\-\s]*(.*?)(?=(?i)education|experience|work|projects|certifications|career|$)",
            r"(?i)skills?/core\s+competencies\s*(.*?)(?=(?i)education|experience|work|projects|certifications|career|$)"
        ],
        
        "education": [
            r"(?i)(?:education|academic\s+background|qualifications|academics|degrees?)[:\-\s]*(.*?)(?=(?i)experience|skills|work|projects|certifications|career|$)",
            r"(?i)education\s*(.*?)(?=(?i)experience|skills|work|projects|certifications|career|$)"
        ],
        
        "experience": [
            r"(?i)(?:experience|work\s+history|employment|professional|career\s+history|work\s+experience|career\s+history)[:\-\s]*(.*?)(?=(?i)education|skills|projects|certifications|teaching|trainings|$)",
            r"(?i)career\s+history\s*(.*?)(?=(?i)education|skills|projects|certifications|teaching|trainings|$)"
        ],
        
        "certifications": [
            r"(?i)(?:certifications?|certificates?|qualifications|licenses?)[:\-\s]*(.*?)(?=(?i)education|experience|skills|basic\s+information|$)",
            r"(?i)certifications\s*(.*?)(?=(?i)education|experience|skills|basic\s+information|$)"
        ]
    }
    
    # Try each pattern for each section
    for section, patterns in section_patterns.items():
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                content = match.group(1).strip()
                print(f"DEBUG: Found {section} section using pattern")
                
                if section == "skills":
                    items = split_skills_string(content)
                else:
                    items = [item.strip() for item in re.split(r'[\n•\-]', content) if item.strip()]
                
                sections[section].extend(items)
                break  # Use first matching pattern
    
    # STRATEGY 3: Fallback extraction for sections not found by regex
    if not sections["skills"]:
        skills_fallback = extract_section_fallback(text, "skills")
        sections["skills"].extend(skills_fallback)
    
    if not sections["education"]:
        education_fallback = extract_section_fallback(text, "education")
        sections["education"].extend(education_fallback)
    
    if not sections["experience"]:
        experience_fallback = extract_section_fallback(text, "experience")
        sections["experience"].extend(experience_fallback)

    # STRATEGY 4: Extract skills from entire text using keyword scanning
    if len(sections["skills"]) < 4:  # If few skills found
        text_skills = extract_skills_from_text_keywords(text)
        sections["skills"].extend(text_skills)
        print(f"DEBUG: Keyword extraction found {len(text_skills)} skills")
    
    # Clean and deduplicate skills
    if sections["skills"]:
        sections["skills"] = clean_skill_list(sections["skills"])
        print(f"🎯 Final skills after cleaning: {len(sections['skills'])} skills")
    
    return sections 

def extract_section_fallback(text: str, section: str) -> List[str]:
    """Robust fallback method for various section headers"""
    section_patterns = {
        "skills": [
            r"Skills/Core Competencies\s*(.*?)(?=Education|Experience|Certifications|$)",
            r"Technical Skills?\s*(.*?)(?=Education|Experience|Work|$)",
            r"Skills?\s*(.*?)(?=Education|Experience|Work|$)"
        ],
        "education": [
            r"Education\s*(.*?)(?=Skills|Experience|Work|$)",
            r"Academic Background\s*(.*?)(?=Skills|Experience|Work|$)",
            r"Qualifications?\s*(.*?)(?=Skills|Experience|Work|$)"
        ],
        "experience": [
            r"Career history\s*(.*?)(?=Education|Skills|Teaching|$)",
            r"Work Experience\s*(.*?)(?=Education|Skills|$)",
            r"Professional Experience\s*(.*?)(?=Education|Skills|$)",
            r"Employment\s*(.*?)(?=Education|Skills|$)"
        ]
    }
    
    if section in section_patterns:
        for pattern in section_patterns[section]:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                content = match.group(1).strip()
                print(f"DEBUG: Fallback found {section} section with pattern: {pattern[:50]}...")
                
                if section == "skills":
                    return split_skills_string(content)
                else:
                    return [item.strip() for item in re.split(r'[\n•\-]', content) if item.strip()]
    
    return []


def parse_education_section(content: str) -> List[str]:
    """Parse education section focusing on degree information"""
    items = []
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    
    current_item = ""
    for line in lines:
        # Look for degree patterns
        if re.search(r'(?:bachelor|master|msc?|bsc?|phd|degree|diploma|certificate|\.\d{4}|\d{4}\s*\-)', line, re.I):
            if current_item:
                items.append(current_item.strip())
            current_item = line
        elif current_item and line and len(line) < 100:
            current_item += " " + line
        elif line and len(line) < 150:  # Reasonable length for education items
            items.append(line)
    
    if current_item:
        items.append(current_item.strip())
    
    return items if items else [item.strip() for item in re.split(r'[\n•\-]', content) if item.strip() and len(item.strip()) < 200] 


def extract_skills_from_text_keywords(text: str) -> List[str]:
    """Extract skills by scanning entire text for keywords"""
    skills_found = set()
    
    # Common technical skills
    technical_skills = [
        'cyber security', 'ethical hacking', 'penetration testing', 'vulnerability assessments',
        'security risk assessment', 'server hardening', 'application hardening', 'security baseline configuration',
        'is audit', 'information security', 'data protection', 'vapt', 'risk analysis',
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
    
    print(f"DEBUG: split_skills_string input: {skills_text[:200]}...")
    
    # FIRST: Try to extract bullet points with multi-word skills
    lines = [line.strip() for line in skills_text.split('\n') if line.strip()]
    
    bullet_skills = []
    for line in lines:
        # Skip lines that are too long (paragraphs)
        if len(line) > 80:
            continue
            
        # Remove ALL types of bullets including ▪ 
        clean_line = re.sub(r'^[\-\•\*\–\—\▪]\s*', '', line)
        
        # Check if this looks like a skill (not a sentence, not too long)
        if (len(clean_line) <= 50 and 
            not re.search(r'[.!?]\s*[A-Z]', clean_line) and  # Not a sentence
            not clean_line.endswith('.') and  # Not ending with period
            clean_line and not clean_line.isdigit() and
            len(clean_line) > 2):  # At least 3 characters
            
            skill = clean_line.strip()
            if skill:
                bullet_skills.append(skill)
    
    # If we found good bullet skills, use them
    if bullet_skills:
        print(f"DEBUG: Found {len(bullet_skills)} bullet skills: {bullet_skills}")
        return bullet_skills
    
    # SECOND: If no bullets found, use SIMPLE space-based splitting but preserve multi-word
    skills = []
    lines = [line.strip() for line in skills_text.split('\n') if line.strip()]
    
    for line in lines:
        # Remove bullets
        clean_line = re.sub(r'^[\-\•\*\–\—\▪]\s*', '', line)
        
        # If line is short and looks like skills, use the whole line
        if len(clean_line) <= 50 and len(clean_line) > 2:
            skills.append(clean_line)
        else:
            # Fallback to your original delimiter approach
            delimiters = [',', ';', '/', '|', '&']
            for delimiter in delimiters:
                if delimiter in clean_line:
                    parts = clean_line.split(delimiter)
                    for part in parts:
                        skill = part.strip()
                        if skill and len(skill) > 2 and not skill.isdigit():
                            skills.append(skill)
                    break
            else:
                # If no delimiters, try to preserve multi-word skills
                # Look for patterns like "Cyber Security", "Ethical Hacking"
                potential_skills = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+|[A-Z][a-z]+', clean_line)
                for skill in potential_skills:
                    if len(skill) > 2 and len(skill) <= 30:
                        skills.append(skill)
    
    # Clean up the skills
    cleaned_skills = []
    for skill in skills:
        skill = re.sub(r'^\W+|\W+$', '', skill)  # Remove surrounding punctuation
        if skill and len(skill) > 2:
            cleaned_skills.append(skill)
    
    print(f"DEBUG: Final skills from split_skills_string: {cleaned_skills}")
    return cleaned_skills

def split_skills_by_uppercase(text: str) -> List[str]:
    skills = re.findall(r'[A-Z][a-z]+|[A-Z]+(?=[A-Z]|$)', text)
    return [skill.strip() for skill in skills if skill.strip()]