import re
from typing import Dict, List
from .text_cleaner import clean_skill_list
from .pdf_table_extractor import extract_skills_from_pdf_tables

def preprocess_text_for_sections(text: str) -> str:
    """
    Pre-process text to make section detection more reliable
    """
    lines = text.split('\n')
    processed_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Detect and mark section headers more reliably
        if (line.upper() in ["PROFESSIONAL SKILLS", "TECHNICAL SKILLS", "SKILLS", "COMPETENCIES"] or
            re.search(r'(?i)^(skills?|technical skills?|professional skills?)$', line)):
            processed_lines.append("")  # Blank line before
            processed_lines.append(line.upper())  # Standardize case
            processed_lines.append("")  # Blank line after
        else:
            processed_lines.append(line)
    
    return '\n'.join(processed_lines)

def enhanced_extract_sections(text: str, file_path: str = None) -> Dict[str, List[str]]:
    """
    Enhanced section extraction that works for ALL resume types
    """
     # PRE-PROCESS TEXT FIRST
    text = preprocess_text_for_sections(text)

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
        # More flexible patterns for different resume formats
        r"(?i)(?:skills?/core\s+competencies|skills?|technical\s+skills?|technologies|expertise|competencies|core\s+competencies|proficiencies|professional\s+skills?)[:\-\s]*(.*?)(?=(?i)education|experience|work|projects|certifications|career|language|summary|$)",
        r"(?i)skills?/core\s+competencies\s*(.*?)(?=(?i)education|experience|work|projects|certifications|career|language|summary|$)",
        # Additional pattern for bullet-style skills
        r"(?i)(?:skills?|technical\s+skills?)[\s\n]*(?:[\-\•].*?)(?=(?i)education|experience|work|projects|certifications|career|language|summary|$)",
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

def extract_skills_section_accurate(text: str) -> str:
    """
    More accurate skills section extraction that finds the actual skills content
    """
    # Look for skills section with clear boundaries
    skills_patterns = [
        # Pattern 1: Standard skills section with header
        r'(?i)(?:^|\n)(?:PROFESSIONAL SKILLS|TECHNICAL SKILLS|SKILLS|COMPETENCIES)\s*\n\s*\n(.*?)(?=\n\s*\n(?:EDUCATION|EXPERIENCE|WORK|PROJECTS|CERTIFICATIONS|LANGUAGES|$))',
        # Pattern 2: Skills section with bullets immediately after
        r'(?i)(?:^|\n)(?:PROFESSIONAL SKILLS|TECHNICAL SKILLS|SKILLS|COMPETENCIES)\s*\n(.*?)(?=\n\s*(?:EDUCATION|EXPERIENCE|WORK|PROJECTS|CERTIFICATIONS|LANGUAGES|$))',
        # Pattern 3: Fallback - skills with bullet points
        r'(?i)(?:^|\n)(?:PROFESSIONAL SKILLS|TECHNICAL SKILLS|SKILLS|COMPETENCIES)(.*?)(?=[\-\•]\s*\w)',
    ]
    
    for pattern in skills_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            content = match.group(1).strip()
            # Verify this actually contains skills (not project descriptions)
            if any(keyword in content.lower() for keyword in ['programming', 'development', 'database', 'python', 'java', 'sql', 'aws']):
                print(f"DEBUG: Accurate skills section found with pattern")
                return content
            # Also check for bullet points or short lines (skills indicators)
            lines = content.split('\n')
            skill_like_lines = [line for line in lines if len(line.strip()) < 50 and re.search(r'^[\-\•]', line.strip())]
            if len(skill_like_lines) >= 2:  # At least 2 bullet points
                print(f"DEBUG: Skills-like content found with {len(skill_like_lines)} bullet points")
                return content
    
    return ""

def split_skills_string(skills_text: str) -> List[str]:
    """
    IMPROVED: Better handling of nested bullet points and multi-line skills
    """
    if not skills_text:
        return []
    
    print(f"DEBUG: split_skills_string input: {skills_text[:200]}...")
    
    skills = []
    lines = [line.strip() for line in skills_text.split('\n') if line.strip()]
    
    current_skill = ""
    indent_level = 0
    
    for line in lines:
        # Skip paragraph-like text (too long)
        if len(line) > 100:
            continue
            
        # Detect bullet points and their indentation
        bullet_match = re.match(r'^([\-\•\*\–\—\▪]\s*)(.*)', line)
        if bullet_match:
            bullet_indent = len(bullet_match.group(1))
            skill_content = bullet_match.group(2).strip()
            
            # If this is a top-level bullet (main skill category)
            if bullet_indent <= 3:  # Top level bullet
                if current_skill and len(current_skill) <= 50:
                    skills.append(current_skill)
                current_skill = skill_content
                indent_level = bullet_indent
            else:
                # This is a sub-bullet (specific technologies under a category)
                if current_skill:
                    # Append to current category as combined skill
                    combined_skill = f"{current_skill}: {skill_content}"
                    if len(combined_skill) <= 60:
                        skills.append(combined_skill)
        else:
            # No bullet - could be continuation or comma-separated
            if current_skill and len(line) < 50:
                # Check if this continues the previous skill
                if len(current_skill + " " + line) <= 60:
                    current_skill += " " + line
                else:
                    if current_skill and len(current_skill) <= 50:
                        skills.append(current_skill)
                    current_skill = line if len(line) <= 50 else ""
            elif len(line) <= 50 and not re.search(r'[.!?]\s*[A-Z]', line):
                # Standalone skill-like line
                skills.append(line)
    
    # Don't forget the last skill
    if current_skill and len(current_skill) <= 50 and current_skill not in skills:
        skills.append(current_skill)
    
    # If no bullet structure found, fall back to comma/semicolon splitting
    if not skills:
        fallback_text = ' '.join(lines)
        # Try comma separation first
        if ',' in fallback_text:
            parts = [part.strip() for part in fallback_text.split(',')]
            skills.extend([p for p in parts if 2 < len(p) <= 50])
        else:
            # Use simple line-based approach
            skills.extend([line for line in lines if 2 < len(line) <= 50])
    
    # Final cleanup
    cleaned_skills = []
    for skill in skills:
        skill = re.sub(r'^\W+|\W+$', '', skill)  # Remove surrounding punctuation
        skill = re.sub(r'\s+', ' ', skill)  # Normalize spaces
        if skill and 2 < len(skill) <= 60 and not skill.isdigit():
            cleaned_skills.append(skill)
    
    print(f"DEBUG: Final skills from split_skills_string: {cleaned_skills}")
    return cleaned_skills

def split_skills_by_uppercase(text: str) -> List[str]:
    skills = re.findall(r'[A-Z][a-z]+|[A-Z]+(?=[A-Z]|$)', text)
    return [skill.strip() for skill in skills if skill.strip()]