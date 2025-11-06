# 🎯 AI Resume Analyzer Pro - Final Year Project

## 📋 Project Overview

An advanced, production-ready Resume Analysis and Skill Gap Detection system built with modern technologies. This system uses AI/ML to parse resumes, extract candidate information, and perform intelligent skill matching against industry-standard job roles.

### 🌟 Key Features

#### Core Functionality
- **🔍 Advanced Resume Parsing** - Multi-strategy PDF/DOCX parsing with OCR fallback for scanned documents
- **🧠 AI-Powered Skill Extraction** - Machine learning-based skill detection and categorization
- **🎯 Intelligent Job Matching** - Automatic role prediction based on candidate skills
- **📊 Skill Gap Analysis** - Comprehensive gap analysis showing matched and missing skills
- **💾 Cloud Database** - Supabase PostgreSQL for data persistence and scalability

#### User Features
- **🔐 User Authentication** - Secure sign-up/sign-in with email/password
- **📁 Resume History** - Save and manage multiple resume analyses
- **📈 Analytics Dashboard** - Visual insights into skill progress and match scores
- **🎨 Modern UI/UX** - Beautiful, responsive Streamlit interface with custom CSS
- **📱 Cross-Platform** - Works on Windows, macOS, and Linux

#### Technical Features
- **🌐 RESTful Architecture** - Clean separation of concerns
- **🔄 Real-time Analysis** - Instant feedback on resume uploads
- **📦 Modular Design** - Easy to maintain and extend
- **🛡️ Security** - Row-level security policies in database
- **📊 Visualization** - Interactive charts using Plotly

---

## 🏗️ Project Structure

```
career_path_finder/
│
├── app/
│   ├── streamlit_app_enhanced.py    # Enhanced Streamlit application
│   ├── uploads/                     # Temporary upload directory
│   └── requirements.txt
│
├── src/
│   ├── database/                    # Database layer
│   │   ├── __init__.py
│   │   ├── supabase_client.py      # Supabase connection
│   │   ├── auth_service.py         # Authentication logic
│   │   ├── resume_repository.py    # Resume CRUD operations
│   │   └── skill_repository.py     # Skills and roles management
│   │
│   └── parsing/                     # Resume parsing module
│       ├── __init__.py
│       ├── pdf_parser_improved.py   # Cross-platform PDF extraction
│       ├── docx_parser.py           # DOCX file parsing
│       ├── enhanced_parser.py       # Advanced section extraction
│       ├── text_cleaner.py          # Text preprocessing
│       ├── pdf_table_extractor.py   # Table extraction
│       └── ml/
│           ├── skill_matcher.py     # Original skill matching
│           └── skill_matcher_db.py  # Database-integrated matching
│
├── tests/                           # Unit and integration tests
├── demo_samples/                    # Sample resume files
├── .env                            # Environment variables
├── requirements_updated.txt        # Python dependencies
└── README_IMPROVED.md              # This file
```

---

## 🛠️ Technology Stack

### Backend
- **Python 3.8+** - Core programming language
- **Supabase** - PostgreSQL database with built-in authentication
- **PyPDF2 / pdfplumber** - PDF text extraction
- **python-docx** - DOCX file parsing
- **pytesseract** - OCR for scanned documents
- **scikit-learn** - Machine learning for skill matching
- **spaCy / NLTK** - Natural language processing

### Frontend
- **Streamlit** - Modern Python web framework
- **Plotly** - Interactive data visualizations
- **Custom CSS** - Beautiful gradient UI with animations

### Database Schema
```sql
Tables:
- users              # User accounts
- resumes            # Uploaded resumes
- job_roles          # Job role definitions
- skill_gaps         # Analysis results
- skills_database    # Comprehensive skills repository
```

---

## ⚙️ Installation & Setup

### Prerequisites
```bash
- Python 3.8 or higher
- pip package manager
- Supabase account (free tier works)
- Optional: Tesseract OCR for scanned PDFs
```

### Step 1: Clone the Repository
```bash
git clone https://github.com/YOUR-USERNAME/resume_analyzer.git
cd resume_analyzer
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements_updated.txt
```

### Step 4: Configure Environment Variables
Create a `.env` file in the project root:

```env
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

**How to get Supabase credentials:**
1. Go to [supabase.com](https://supabase.com) and create a free account
2. Create a new project
3. Go to Settings → API
4. Copy the URL and anon/public key
5. Paste them into your `.env` file

### Step 5: Database Setup
The database schema is automatically created when you run the application for the first time. It includes:
- User authentication tables
- Resume storage
- Job roles with predefined skills
- Skills database with synonyms
- Analysis history tracking

### Step 6: Run the Application
```bash
streamlit run app/streamlit_app_enhanced.py
```

The application will open in your browser at `http://localhost:8501`

---

## 📖 Usage Guide

### For Users

#### 1. **Create an Account**
   - Click on the "Sign Up" tab
   - Enter your full name, email, and password
   - Click "Sign Up" to create your account

#### 2. **Sign In**
   - Use the "Sign In" tab
   - Enter your credentials
   - Access your personalized dashboard

#### 3. **Upload & Analyze Resume**
   - Navigate to "Upload & Analyze" tab
   - Drag and drop or browse for your resume (PDF/DOCX)
   - Wait for AI analysis (typically 5-10 seconds)
   - View extracted skills, education, and experience

#### 4. **Select Target Role**
   - Choose from 10+ predefined job roles
   - View your match score percentage
   - See matched skills (what you have)
   - See missing skills (what to learn)

#### 5. **Track Progress**
   - Check "My Resumes" tab for upload history
   - View "Analytics" tab for insights
   - See your progress over time
   - Identify skill trends

### For Developers

#### Adding New Job Roles
```python
# Use the Supabase dashboard or SQL editor
INSERT INTO job_roles (role_name, required_skills, category, experience_level)
VALUES (
  'Your New Role',
  '["Skill1", "Skill2", "Skill3"]'::jsonb,
  'Category Name',
  'Junior'
);
```

#### Adding New Skills
```python
from src.database import SkillRepository

skill_repo = SkillRepository()
skill_repo.add_custom_skill(
    skill_name="New Skill",
    category="Programming Languages",
    synonyms=["synonym1", "synonym2"],
    popularity_score=75
)
```

---

## 🎨 UI Improvements

### Custom Styling Features
1. **Gradient Background** - Beautiful purple gradient theme
2. **Animated Cards** - Hover effects on stat cards
3. **Skill Badges** - Color-coded skill tags
4. **Progress Bars** - Visual match score indicators
5. **Responsive Design** - Works on all screen sizes
6. **Custom Buttons** - Styled with gradients and shadows
7. **Interactive Charts** - Plotly visualizations

### Key UI Enhancements
- ✨ Glassmorphism effects
- 🎭 Smooth transitions and animations
- 🎨 Professional color scheme
- 📱 Mobile-friendly responsive layout
- 🖼️ Beautiful typography (Inter font)

---

## 🔒 Security Features

### Database Security
- **Row Level Security (RLS)** enabled on all tables
- Users can only access their own data
- Secure authentication with Supabase Auth
- SQL injection prevention
- Encrypted connections

### Best Practices
- Password hashing by Supabase
- Session management
- Input validation
- Error handling without data leakage

---

## 📊 Database Schema Details

### Users Table
- Stores user profiles and authentication info
- Linked to Supabase Auth

### Resumes Table
- Stores uploaded resume data
- JSON fields for parsed information
- File metadata tracking

### Job Roles Table
- Predefined career paths
- Required skills in JSONB format
- Categorized by industry and experience level

### Skill Gaps Table
- Analysis results storage
- Historical tracking
- Match scores and missing skills

### Skills Database Table
- Comprehensive skill repository
- Synonyms for better matching
- Popularity scores

---

## 🚀 Advanced Features

### Cross-Platform PDF Parsing
```python
# Automatically tries multiple strategies:
1. pdftotext (fastest, for text-based PDFs)
2. PyPDF2 (lightweight Python library)
3. pdfplumber (handles complex layouts)
4. OCR with Tesseract (for scanned documents)
```

### Skill Normalization
```python
# Handles variations:
"Python" == "python" == "py" == "python3"
"Machine Learning" == "ML" == "machine learning"
```

### Analytics Dashboard
- Line charts showing progress over time
- Pie charts for role distribution
- Top performing analyses
- Skill trend tracking

---

## 🧪 Testing

### Run Tests
```bash
pytest tests/
```

### Test Coverage
- Unit tests for parsing modules
- Integration tests for database operations
- End-to-end user workflow tests

---

## 🎓 Learning Outcomes (For Final Year Project)

### Technical Skills Demonstrated
1. **Full-Stack Development** - Backend + Frontend + Database
2. **Machine Learning** - Skill extraction and matching
3. **Database Design** - Normalized schema with relationships
4. **Authentication** - Secure user management
5. **UI/UX Design** - Modern, responsive interface
6. **Cloud Integration** - Supabase cloud database
7. **Error Handling** - Robust exception management
8. **Code Organization** - Modular, maintainable architecture

### Project Management
- Version control with Git
- Documentation
- Testing strategies
- Deployment considerations

---

## 📚 API Documentation

### Database API

#### AuthService
```python
auth = AuthService()

# Sign up
result = auth.sign_up("email@example.com", "password", "Full Name")

# Sign in
result = auth.sign_in("email@example.com", "password")

# Get current user
user = auth.get_current_user()
```

#### ResumeRepository
```python
repo = ResumeRepository()

# Save resume
resume = repo.save_resume(
    user_id="uuid",
    filename="resume.pdf",
    file_type="pdf",
    raw_text="...",
    parsed_data={...},
    file_size=12345
)

# Get user resumes
resumes = repo.get_user_resumes(user_id)

# Get statistics
stats = repo.get_resume_statistics(user_id)
```

#### SkillRepository
```python
skills = SkillRepository()

# Get all job roles
roles = skills.get_all_job_roles()

# Get role details
role = skills.get_job_role_details("Data Scientist")

# Search skills
results = skills.search_skills("python")
```

---

## 🔧 Troubleshooting

### Common Issues

**Issue:** Database connection error
```
Solution: Check your .env file has correct Supabase credentials
```

**Issue:** PDF parsing fails
```
Solution: Install Tesseract OCR for scanned PDFs
Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
Mac: brew install tesseract
Linux: sudo apt-get install tesseract-ocr
```

**Issue:** No skills detected
```
Solution:
1. Ensure resume has clear section headers (Skills, Experience, etc.)
2. Try different file format (PDF vs DOCX)
3. Check if resume is scanned (OCR required)
```

---

## 🎯 Future Enhancements

### Potential Improvements
1. **Resume Builder** - Help users create better resumes
2. **Job Recommendations** - Match users with job postings
3. **Skill Courses** - Recommend courses for missing skills
4. **ATS Score** - Check resume compatibility with ATS systems
5. **Multi-language Support** - Support non-English resumes
6. **API Integration** - Connect with LinkedIn, Indeed, etc.
7. **Email Notifications** - Send analysis reports via email
8. **PDF Export** - Generate professional reports
9. **Bulk Upload** - Process multiple resumes at once
10. **Admin Dashboard** - Manage users and roles

---

## 👥 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👤 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/yourprofile)
- Email: your.email@example.com

---

## 🙏 Acknowledgments

- Streamlit for the amazing web framework
- Supabase for the backend infrastructure
- The open-source community for various libraries
- Academic advisors and project guides

---

## 📞 Support

For support, email your.email@example.com or open an issue on GitHub.

---

## ⭐ Show Your Support

Give a ⭐️ if this project helped you!

---

**Made with ❤️ for Final Year Project Evaluation**
