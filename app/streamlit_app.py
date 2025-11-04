from __future__ import annotations
from pathlib import Path
import sys
import time
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
import json

PROJ_ROOT = Path(__file__).resolve().parents[1]
if str(PROJ_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJ_ROOT))

try:
    from src.parsing.ml.skill_matcher_db import analyze_resume
    from src.database import AuthService, ResumeRepository, SkillRepository, init_supabase
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

UPLOADS_DIR = PROJ_ROOT / "app" / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# ===== CONFIGURATION =====
# Update these with your actual links
LINKEDIN_URL = "https://www.linkedin.com/in/yourprofile"
GITHUB_URL = "https://github.com/yourusername"
PRODUCT_NAME = "AI Resume Analyzer Pro"
CURRENT_YEAR = "2025"

st.set_page_config(
    page_title="AI Resume Analyzer Pro",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ✅ ENHANCED MODERN UI WITH FOOTER
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

    * {
        font-family: 'Poppins', sans-serif;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }

    /* Optimize for laptop screens (1366px - 1920px) */
    .main .block-container {
        max-width: 1400px;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    /* Better font sizes for laptop screens */
    body {
        font-size: 15px;
        line-height: 1.6;
    }

    h1 {
        font-size: 2.2rem;
        line-height: 1.3;
    }

    h2 {
        font-size: 1.8rem;
        line-height: 1.3;
    }

    h3 {
        font-size: 1.4rem;
    }

    /* ============================================
       LOGIN PAGE STYLING - Modern Card Design
    ============================================ */
    .login-container {
        max-width: 480px;
        margin: 40px auto 20px auto;
        background: white;
        border-radius: 20px;
        padding: 45px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        animation: fadeInUp 0.6s ease;
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .login-header {
        text-align: center;
        margin-bottom: 30px;
    }

    .login-title {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }

    .login-subtitle {
        color: #666;
        font-size: 1rem;
        font-weight: 400;
    }

    /* ============================================
       FOOTER STYLING - Auth Pages (Login/Signup)
    ============================================ */
    .auth-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 25px 40px;
        border-top: 1px solid rgba(102, 126, 234, 0.2);
        z-index: 1000;
        box-shadow: 0 -5px 20px rgba(0, 0, 0, 0.1);
    }

    .auth-footer-content {
        max-width: 1400px;
        margin: 0 auto;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 15px;
    }

    .footer-links {
        display: flex;
        gap: 25px;
        align-items: center;
        flex-wrap: wrap;
    }

    .footer-link {
        color: #667eea;
        text-decoration: none;
        font-weight: 500;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 5px;
    }

    .footer-link:hover {
        color: #764ba2;
        transform: translateY(-2px);
    }

    .footer-divider {
        color: #d1d5db;
        margin: 0 5px;
    }

    .footer-copyright {
        color: #6b7280;
        font-size: 0.85rem;
        font-weight: 400;
    }

    .privacy-notice {
        max-width: 1200px;
        margin: 20px auto;
        background: rgba(255, 255, 255, 0.95);
        padding: 20px 30px;
        border-radius: 12px;
        text-align: center;
        font-size: 0.85rem;
        color: #4b5563;
        line-height: 1.6;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }

    .privacy-notice strong {
        color: #667eea;
        font-weight: 600;
    }

    /* ============================================
       DASHBOARD FOOTER
    ============================================ */
    .dashboard-footer {
        background: white;
        padding: 30px 40px;
        margin: 40px -40px -40px -40px;
        border-top: 2px solid #f3f4f6;
        border-radius: 0 0 20px 20px;
    }

    .dashboard-footer-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 20px;
    }

    .social-links {
        display: flex;
        gap: 20px;
        align-items: center;
    }

    .social-link {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 10px 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-decoration: none;
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }

    .social-link:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        color: white;
    }

    .footer-help-links {
        display: flex;
        gap: 20px;
        align-items: center;
        flex-wrap: wrap;
    }

    .help-link {
        color: #667eea;
        text-decoration: none;
        font-weight: 500;
        font-size: 0.9rem;
        transition: all 0.3s ease;
    }

    .help-link:hover {
        color: #764ba2;
    }

    /* ============================================
       MODAL STYLING (for Privacy Policy, Terms, etc.)
    ============================================ */
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(5px);
        z-index: 9998;
        display: none;
    }

    .modal-overlay.active {
        display: block;
    }

    .modal-content {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        padding: 40px;
        border-radius: 20px;
        max-width: 700px;
        max-height: 80vh;
        overflow-y: auto;
        z-index: 9999;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
        display: none;
    }

    .modal-content.active {
        display: block;
    }

    .modal-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 20px;
    }

    .modal-close {
        position: absolute;
        top: 20px;
        right: 20px;
        background: #ef4444;
        color: white;
        border: none;
        border-radius: 50%;
        width: 35px;
        height: 35px;
        font-size: 1.2rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .modal-close:hover {
        background: #dc2626;
        transform: rotate(90deg);
    }

    /* ============================================
       DASHBOARD STYLING - Modern Layout
    ============================================ */
    .dashboard-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 40px;
        background: rgba(255, 255, 255, 0.98);
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
        margin-top: 20px;
        margin-bottom: 20px;
        min-height: calc(100vh - 100px);
    }

    /* Welcome Banner */
    .welcome-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }

    .welcome-banner h2 {
        margin: 0 0 8px 0;
        font-size: 1.9rem;
        font-weight: 600;
        color: white !important;
        border: none !important;
        padding: 0 !important;
    }

    .welcome-banner p {
        margin: 0;
        opacity: 0.95;
        font-size: 1.05rem;
    }

    /* Stats Grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 20px;
        margin-bottom: 30px;
    }

    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 28px;
        border-radius: 15px;
        color: white;
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
        border: none;
    }

    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
    }

    .stat-number {
        font-size: 2.8rem;
        font-weight: 800;
        margin: 12px 0;
    }

    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 500;
    }

    /* Section Headers */
    .section-header {
        font-size: 1.4rem;
        font-weight: 600;
        color: #1f2937;
        margin: 30px 0 20px 0;
        padding-bottom: 12px;
        border-bottom: 2px solid #e5e7eb;
    }

    /* Buttons - Modern Style */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 13px 32px;
        font-weight: 600;
        font-size: 1.05rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        width: 100%;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }

    /* Tabs - Clean Design */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #f9fafb;
        padding: 10px;
        border-radius: 12px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 52px;
        background: transparent;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 1rem;
        color: #6b7280;
        border: none;
    }

    .stTabs [aria-selected="true"] {
        background: white;
        color: #667eea;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }

    /* Input Fields - Modern */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e5e7eb;
        padding: 13px 18px;
        font-size: 1.05rem;
        transition: all 0.3s ease;
    }

    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }

    /* File Uploader */
    .uploadedFile {
        background: #f9fafb;
        border: 2px dashed #d1d5db;
        border-radius: 12px;
        padding: 22px;
        transition: all 0.3s ease;
    }

    .uploadedFile:hover {
        border-color: #667eea;
        background: #f0f4ff;
    }

    /* Skill Badges */
    .skill-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 9px 18px;
        border-radius: 20px;
        margin: 6px;
        font-weight: 600;
        font-size: 0.9rem;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }

    .skill-badge-missing {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    }

    /* Message Boxes */
    .success-box {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        padding: 18px 22px;
        border-radius: 12px;
        color: white;
        margin: 15px 0;
        font-weight: 500;
        font-size: 1rem;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }

    .warning-box {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        padding: 18px 22px;
        border-radius: 12px;
        color: white;
        margin: 15px 0;
        font-weight: 500;
        font-size: 1rem;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
    }

    .info-box {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        padding: 18px 22px;
        border-radius: 12px;
        color: white;
        margin: 15px 0;
        font-weight: 500;
        font-size: 1rem;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }

    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: #f9fafb;
        border-radius: 10px;
        font-weight: 600;
        font-size: 1rem;
        color: #374151;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.9rem;
        font-weight: 700;
        color: #667eea;
    }

    /* Remove padding from block container */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        max-width: 100%;
    }

    /* Content area cards */
    .content-card {
        background: white;
        border-radius: 15px;
        padding: 28px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }

    /* Selectbox */
    .stSelectbox > div > div {
        border-radius: 10px;
        border: 2px solid #e5e7eb;
        font-size: 1.05rem;
    }

    /* Sign out button */
    .sign-out-btn button {
        background: white !important;
        color: #667eea !important;
        border: 2px solid #667eea !important;
        padding: 10px 22px !important;
        font-size: 0.95rem !important;
    }

    .sign-out-btn button:hover {
        background: #667eea !important;
        color: white !important;
    }

    /* Responsive adjustments */
    @media (max-width: 1200px) {
        .stats-grid {
            grid-template-columns: repeat(2, 1fr);
        }
        
        .auth-footer-content {
            flex-direction: column;
            text-align: center;
        }
    }

    /* Add spacing at bottom for auth footer */
    .auth-page-spacer {
        height: 120px;
    }
</style>
""", unsafe_allow_html=True)

def show_privacy_modal():
    """Privacy Policy Modal Content"""
    return """
    <div class="modal-content" id="privacyModal">
        <button class="modal-close" onclick="closeModal('privacyModal')">×</button>
        <div class="modal-header">🔒 Privacy Policy</div>
        <div style="color: #4b5563; line-height: 1.8;">
            <h3 style="color: #667eea; margin-top: 20px;">Data Collection & Storage</h3>
            <p><strong>Your Privacy Matters:</strong> We take your data security seriously. Here's what you need to know:</p>
            
            <h4 style="color: #374151; margin-top: 15px;">Without an Account:</h4>
            <ul style="margin-left: 20px;">
                <li>✅ Resumes are processed in real-time</li>
                <li>✅ No permanent storage of your documents</li>
                <li>✅ Files automatically deleted after analysis</li>
                <li>✅ Zero data retention policy</li>
            </ul>
            
            <h4 style="color: #374151; margin-top: 15px;">With an Account:</h4>
            <ul style="margin-left: 20px;">
                <li>📊 Analysis history saved for your reference</li>
                <li>🔐 Data encrypted at rest and in transit</li>
                <li>👤 Only you can access your uploaded resumes</li>
                <li>🗑️ Delete your data anytime from dashboard</li>
            </ul>
            
            <h3 style="color: #667eea; margin-top: 20px;">Security Measures</h3>
            <ul style="margin-left: 20px;">
                <li>🔒 SSL/TLS encryption for all transfers</li>
                <li>🛡️ Industry-standard database security (Supabase)</li>
                <li>🔑 Password hashing with bcrypt</li>
                <li>🚫 No third-party data sharing</li>
            </ul>
            
            <h3 style="color: #667eea; margin-top: 20px;">Your Rights</h3>
            <p>You have the right to:</p>
            <ul style="margin-left: 20px;">
                <li>Access your data at any time</li>
                <li>Export your analysis history</li>
                <li>Delete your account and all associated data</li>
                <li>Opt-out of any future communications</li>
            </ul>
            
            <p style="margin-top: 20px;"><strong>Last Updated:</strong> January 2025</p>
            <p><strong>Contact:</strong> <a href="javascript:void(0)" onclick="window.open('""" + LINKEDIN_URL + """', '_blank')" style="color: #667eea;">Reach us on LinkedIn</a></p>
        </div>
    </div>
    """

def show_terms_modal():
    """Terms of Service Modal Content"""
    return """
    <div class="modal-content" id="termsModal">
        <button class="modal-close" onclick="closeModal('termsModal')">×</button>
        <div class="modal-header">📜 Terms of Service</div>
        <div style="color: #4b5563; line-height: 1.8;">
            <h3 style="color: #667eea; margin-top: 20px;">Acceptable Use</h3>
            <p>By using AI Resume Analyzer Pro, you agree to:</p>
            <ul style="margin-left: 20px;">
                <li>✅ Upload only your own resumes or resumes you have permission to analyze</li>
                <li>✅ Use the service for legitimate career development purposes</li>
                <li>✅ Not attempt to reverse-engineer our AI models</li>
                <li>✅ Not upload malicious files or attempt security breaches</li>
            </ul>
            
            <h3 style="color: #667eea; margin-top: 20px;">Service Limitations</h3>
            <ul style="margin-left: 20px;">
                <li>📄 File size limit: 10MB per resume</li>
                <li>📊 Supported formats: PDF, DOCX</li>
                <li>⚡ Analysis typically completes in 10-30 seconds</li>
                <li>🔍 OCR available for scanned documents</li>
            </ul>
            
            <h3 style="color: #667eea; margin-top: 20px;">Disclaimer</h3>
            <p>Our AI provides <strong>guidance and suggestions</strong> only. We do not guarantee:</p>
            <ul style="margin-left: 20px;">
                <li>Job placement or interview opportunities</li>
                <li>100% accuracy in skill extraction</li>
                <li>Specific outcomes from using our recommendations</li>
            </ul>
            
            <p style="margin-top: 20px;">Results should be used as one tool in your career development strategy.</p>
            
            <h3 style="color: #667eea; margin-top: 20px;">Account Termination</h3>
            <p>We reserve the right to suspend or terminate accounts that:</p>
            <ul style="margin-left: 20px;">
                <li>Violate these terms</li>
                <li>Engage in abusive behavior</li>
                <li>Attempt to exploit the service</li>
            </ul>
            
            <p style="margin-top: 20px;"><strong>Effective Date:</strong> January 2025</p>
        </div>
    </div>
    """

def show_help_modal():
    """Help Center Modal Content"""
    return """
    <div class="modal-content" id="helpModal">
        <button class="modal-close" onclick="closeModal('helpModal')">×</button>
        <div class="modal-header">💡 Help Center</div>
        <div style="color: #4b5563; line-height: 1.8;">
            <h3 style="color: #667eea; margin-top: 20px;">Getting Started</h3>
            <p><strong>1. Upload Your Resume</strong></p>
            <ul style="margin-left: 20px;">
                <li>Click "Upload & Analyze" tab</li>
                <li>Select PDF or DOCX file (max 10MB)</li>
                <li>Wait for AI analysis to complete</li>
            </ul>
            
            <p><strong>2. Review Your Analysis</strong></p>
            <ul style="margin-left: 20px;">
                <li>View extracted skills, experience, and education</li>
                <li>See top matching job roles with scores</li>
                <li>Select a target role for detailed gap analysis</li>
            </ul>
            
            <p><strong>3. Understand Your Results</strong></p>
            <ul style="margin-left: 20px;">
                <li>✅ <strong>Matched Skills:</strong> Skills you have for the role</li>
                <li>❌ <strong>Missing Skills:</strong> Skills to learn for better match</li>
                <li>📊 <strong>Match Score:</strong> Percentage fit for the role</li>
            </ul>
            
            <h3 style="color: #667eea; margin-top: 20px;">Common Issues</h3>
            
            <p><strong>Q: My resume isn't parsing correctly?</strong></p>
            <p>A: Ensure your resume is:
                <ul style="margin-left: 20px;">
                    <li>Well-formatted with clear sections</li>
                    <li>Not password-protected</li>
                    <li>Under 10MB in size</li>
                    <li>In PDF or DOCX format</li>
                </ul>
            </p>
            
            <p><strong>Q: Skills are missing?</strong></p>
            <p>A: Our AI recognizes 200+ common skills. If yours is specialized:
                <ul style="margin-left: 20px;">
                    <li>Check spelling and formatting</li>
                    <li>Use industry-standard skill names</li>
                    <li>List skills in a clear "Skills" section</li>
                </ul>
            </p>
            
            <p><strong>Q: Match score seems low?</strong></p>
            <p>A: This indicates skill gap, not quality! It means:
                <ul style="margin-left: 20px;">
                    <li>The role requires skills you don't have yet</li>
                    <li>You should focus on learning the missing skills</li>
                    <li>Consider roles with higher match scores</li>
                </ul>
            </p>
            
            <h3 style="color: #667eea; margin-top: 20px;">Tips for Better Results</h3>
            <ul style="margin-left: 20px;">
                <li>📝 Use standard resume section headers (Skills, Experience, Education)</li>
                <li>🎯 List technical skills explicitly</li>
                <li>📅 Include dates for education and experience</li>
                <li>🏢 Mention company names and job titles clearly</li>
            </ul>
            
            <p style="margin-top: 20px;"><strong>Still need help?</strong></p>
            <p><a href="javascript:void(0)" onclick="window.open('""" + LINKEDIN_URL + """', '_blank')" style="color: #667eea; font-weight: 600;">Contact us on LinkedIn →</a></p>
        </div>
    </div>
    """

# JavaScript for modal functionality
modal_js = """
<script>
function openModal(modalId) {
    document.getElementById(modalId).classList.add('active');
    document.getElementById('modalOverlay').classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
    document.getElementById('modalOverlay').classList.remove('active');
    document.body.style.overflow = 'auto';
}

// Close modal when clicking overlay
document.addEventListener('click', function(e) {
    if (e.target.id === 'modalOverlay') {
        document.querySelectorAll('.modal-content').forEach(modal => {
            modal.classList.remove('active');
        });
        document.getElementById('modalOverlay').classList.remove('active');
        document.body.style.overflow = 'auto';
    }
});
</script>
"""

def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'page' not in st.session_state:
        st.session_state.page = 'auth'
    if 'auth_service' not in st.session_state:
        try:
            init_supabase()
            st.session_state.auth_service = AuthService()
            st.session_state.resume_repo = ResumeRepository()
            st.session_state.skill_repo = SkillRepository()
        except Exception as e:
            st.error(f"Database connection error: {e}")
            st.stop()

def show_auth_footer():
    """Show footer for authentication pages"""
    st.markdown("""
    <div class="privacy-notice">
        <strong>🔒 Your Privacy Guaranteed:</strong> Without an account, your resume is processed in real-time and 
        <strong>never stored permanently</strong>. With an account, your data is encrypted and you maintain full control. 
        We never share your information with third parties.
    </div>
    
    <div class="auth-footer">
        <div class="auth-footer-content">
            <div class="footer-links">
                <a href="javascript:void(0)" onclick="openModal('privacyModal')" class="footer-link">
                    🔒 Privacy Policy
                </a>
                <span class="footer-divider">|</span>
                <a href="javascript:void(0)" onclick="openModal('termsModal')" class="footer-link">
                    📜 Terms of Service
                </a>
                <span class="footer-divider">|</span>
                <a href="javascript:void(0)" onclick="window.open('""" + LINKEDIN_URL + """', '_blank')" class="footer-link">
                    💬 Contact Support
                </a>
            </div>
            <div class="footer-copyright">
                © """ + CURRENT_YEAR + """ """ + PRODUCT_NAME + """ • Built with ❤️ for Career Success
            </div>
        </div>
    </div>
    
    <div class="modal-overlay" id="modalOverlay"></div>
    """ + show_privacy_modal() + show_terms_modal() + show_help_modal() + modal_js + """
    
    <div class="auth-page-spacer"></div>
    """, unsafe_allow_html=True)

def show_dashboard_footer():
    """Show footer for dashboard pages"""
    st.markdown("""
    <div class="dashboard-footer">
        <div class="dashboard-footer-content">
            <div class="social-links">
                <a href="""" + GITHUB_URL + """" target="_blank" class="social-link">
                    <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                    </svg>
                    GitHub
                </a>
                <a href="``` + LINKEDIN_URL + ```" target="_blank" class="social-link">
                    <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
                    </svg>
                    LinkedIn
                </a>
            </div>
            
            <div class="footer-help-links">
                <a href="javascript:void(0)" onclick="openModal('helpModal')" class="help-link">
                    💡 Help Center
                </a>
                <span class="footer-divider">|</span>
                <a href="javascript:void(0)" onclick="window.open('""" + LINKEDIN_URL + """', '_blank')" class="help-link">
                    📞 Contact Sales
                </a>
                <span class="footer-divider">|</span>
                <a href="javascript:void(0)" onclick="openModal('privacyModal')" class="help-link">
                    🔒 Privacy
                </a>
            </div>
        </div>
    </div>
    
    <div class="modal-overlay" id="modalOverlay"></div>
    """ + show_privacy_modal() + show_terms_modal() + show_help_modal() + modal_js + """
    """, unsafe_allow_html=True)

def show_auth_page():
    """Show modern authentication page"""
    # Center the login card
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="login-container">
            <div class="login-header">
                <div class="login-title">🎯 AI Resume Analyzer Pro</div>
                <div class="login-subtitle">Advanced Resume Analysis & Skill Gap Detection</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Sign In", "📝 Sign Up"])
        
        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("signin_form", clear_on_submit=False):
                email = st.text_input("📧 Email Address", placeholder="your.email@example.com", key="signin_email")
                password = st.text_input("🔒 Password", type="password", placeholder="Enter your password", key="signin_password")
                
                st.markdown("<br>", unsafe_allow_html=True)
                submit = st.form_submit_button("Sign In", use_container_width=True)
                
                if submit:
                    if email and password:
                        with st.spinner("Signing in..."):
                            result = st.session_state.auth_service.sign_in(email, password)
                            if result['success']:
                                st.session_state.authenticated = True
                                st.session_state.user = result['user']
                                st.session_state.page = 'dashboard'
                                st.success("✅ " + result['message'])
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("❌ " + result['message'])
                    else:
                        st.warning("⚠️ Please fill in all fields")
        
        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("signup_form", clear_on_submit=False):
                full_name = st.text_input("👤 Full Name", placeholder="John Doe", key="signup_name")
                email = st.text_input("📧 Email Address", placeholder="your.email@example.com", key="signup_email")
                password = st.text_input("🔒 Password", type="password", placeholder="Choose a strong password", key="signup_password")
                password_confirm = st.text_input("🔒 Confirm Password", type="password", placeholder="Re-enter your password", key="signup_confirm")
                
                st.markdown("<br>", unsafe_allow_html=True)
                submit = st.form_submit_button("Create Account", use_container_width=True)
                
                if submit:
                    if all([full_name, email, password, password_confirm]):
                        if password == password_confirm:
                            if len(password) >= 6:
                                with st.spinner("Creating account..."):
                                    result = st.session_state.auth_service.sign_up(email, password, full_name)
                                    if result['success']:
                                        st.success("✅ " + result['message'])
                                        st.info("💡 Please use the Sign In tab to access your account")
                                    else:
                                        st.error("❌ " + result['message'])
                            else:
                                st.error("❌ Password must be at least 6 characters")
                        else:
                            st.error("❌ Passwords do not match!")
                    else:
                        st.warning("⚠️ Please fill in all fields")
    
    # Show footer for auth page
    show_auth_footer()

def show_dashboard():
    """Show modern dashboard"""
    st.markdown('<div class="dashboard-container">', unsafe_allow_html=True)
    
    # Header with sign out
    col1, col2 = st.columns([4, 1])
    with col1:
        user_name = st.session_state.user.email.split('@')[0].title() if st.session_state.user else "User"
        st.markdown(f"""
        <div class="welcome-banner">
            <h2>👋 Welcome back, {user_name}!</h2>
            <p>Track your resume analysis, match scores, and skill development journey</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="sign-out-btn">', unsafe_allow_html=True)
        if st.button("🚪 Sign Out", use_container_width=True):
            st.session_state.auth_service.sign_out()
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.page = 'auth'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Statistics Cards
    stats = st.session_state.resume_repo.get_resume_statistics(st.session_state.user.id)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">📁 Total Resumes</div>
            <div class="stat-number">{stats['total_resumes']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">📊 Analyses Done</div>
            <div class="stat-number">{stats['total_analyses']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">🎯 Avg Match</div>
            <div class="stat-number">{stats['average_match_score']}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">💡 Unique Skills</div>
            <div class="stat-number">{stats['unique_skills']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["📤 Upload & Analyze", "📁 My Resumes", "📊 Analytics"])
    
    with tab1:
        show_upload_section()
    
    with tab2:
        show_my_resumes()
    
    with tab3:
        show_analytics()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Show footer for dashboard
    show_dashboard_footer()

def show_upload_section():
    """Upload and analyze resume section"""
    st.markdown('<div class="section-header">📤 Upload Your Resume</div>', unsafe_allow_html=True)
    st.markdown("**Supports PDF and DOCX files. Scanned documents automatically processed with OCR.**")
    
    uploaded = st.file_uploader(
        "Choose your resume file",
        type=["pdf", "docx"],
        help="Upload your resume for AI-powered analysis"
    )
    
    if uploaded:
        ts = time.strftime("%Y%m%d-%H%M%S")
        safe_name = uploaded.name.replace(" ", "_")
        saved_path = UPLOADS_DIR / f"{ts}__{safe_name}"
        
        with saved_path.open("wb") as f:
            f.write(uploaded.getbuffer())
        
        st.markdown('<div class="success-box">✅ Resume uploaded successfully! Analyzing now...</div>', unsafe_allow_html=True)
        
        with st.spinner("🔍 Analyzing your resume with AI..."):
            progress = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress.progress(i + 1)
            
            roles_map = st.session_state.skill_repo.get_all_job_roles()
            result = analyze_resume(str(saved_path))
            
            resume_record = st.session_state.resume_repo.save_resume(
                user_id=st.session_state.user.id,
                filename=uploaded.name,
                file_type=uploaded.type.split('/')[-1],
                raw_text="",
                parsed_data=result["parsed"],
                file_size=uploaded.size
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown('<div class="section-header">🧩 Extracted Information</div>', unsafe_allow_html=True)
            
            skills = result["parsed"].get("skills", [])
            edu = result["parsed"].get("education", [])
            exp = result["parsed"].get("experience", [])
            
            st.markdown("**💡 Skills Found:**")
            if skills:
                skills_html = " ".join([f'<span class="skill-badge">{skill.title()}</span>' 
                                       for skill in sorted(skills)[:20]])
                st.markdown(skills_html, unsafe_allow_html=True)
                if len(skills) > 20:
                    st.info(f"+ {len(skills) - 20} more skills")
            else:
                st.markdown('<div class="warning-box">⚠️ No skills detected</div>', unsafe_allow_html=True)
            
            st.markdown("<br>**🎓 Education:**")
            if edu:
                for e in edu[:3]:
                    st.write(f"• {e}")
            else:
                st.write("—")
            
            st.markdown("<br>**💼 Experience:**")
            if exp:
                for e in exp[:3]:
                    st.write(f"• {e}")
            else:
                st.write("—")
        
        with col2:
            st.markdown('<div class="section-header">🎯 Job Role Analysis</div>', unsafe_allow_html=True)
            
            preds = result.get("predictions", [])
            if preds:
                st.markdown("**Top Matching Roles:**")
                for role, score in preds[:3]:
                    st.markdown(f"**{role}** — {score:.1f}%")
                    st.progress(score / 100)
                    st.markdown("<br>", unsafe_allow_html=True)
                
                default_role = preds[0][0]
            else:
                default_role = list(roles_map.keys())[0] if roles_map else "Junior Data Scientist"
            
            st.markdown("<br>", unsafe_allow_html=True)
            chosen = st.selectbox(
                "🎯 Select Target Role for Detailed Analysis",
                options=list(roles_map.keys()),
                index=list(roles_map.keys()).index(default_role) if default_role in roles_map else 0
            )
            
            if chosen != result["chosen_role"]:
                with st.spinner("Recalculating..."):
                    result = analyze_resume(str(saved_path), chosen_role=chosen)
            
            matched = result["gap"].get("matched", [])
            missing = result["gap"].get("missing", [])
            match_score = result.get('match_score', 0)
            
            st.markdown(f"<br>**Match Score: {match_score:.1f}%**", unsafe_allow_html=True)
            st.progress(match_score / 100)
            
            if resume_record:
                st.session_state.resume_repo.save_skill_gap_analysis(
                    user_id=st.session_state.user.id,
                    resume_id=resume_record['id'],
                    target_role=chosen,
                    matched_skills=matched,
                    missing_skills=missing,
                    match_score=match_score
                )
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="section-header">✅ Matched Skills</div>', unsafe_allow_html=True)
            if matched:
                matched_html = " ".join([f'<span class="skill-badge">{skill.title()}</span>' 
                                        for skill in sorted(matched)])
                st.markdown(matched_html, unsafe_allow_html=True)
            else:
                st.write("—")
        
        with col2:
            st.markdown('<div class="section-header">❌ Skills to Learn</div>', unsafe_allow_html=True)
            if missing:
                missing_html = " ".join([f'<span class="skill-badge skill-badge-missing">{skill.title()}</span>' 
                                        for skill in sorted(missing)])
                st.markdown(missing_html, unsafe_allow_html=True)
            else:
                st.markdown('<div class="success-box">🎉 Perfect match! No skills missing!</div>', unsafe_allow_html=True)
        
        if saved_path.exists():
            saved_path.unlink()

def show_my_resumes():
    """Show user's uploaded resumes"""
    st.markdown('<div class="section-header">📁 Your Resume History</div>', unsafe_allow_html=True)
    
    resumes = st.session_state.resume_repo.get_user_resumes(st.session_state.user.id)
    
    if not resumes:
        st.markdown('<div class="info-box">📭 No resumes yet. Upload your first resume in the "Upload & Analyze" tab!</div>', unsafe_allow_html=True)
        return
    
    for resume in resumes:
        with st.expander(f"📄 {resume['filename']} — {resume['upload_date'][:10]}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("📦 File Size", f"{resume['file_size'] / 1024:.1f} KB")
            
            with col2:
                skills_count = len(json.loads(resume['parsed_skills'])) if isinstance(resume['parsed_skills'], str) else len(resume['parsed_skills'])
                st.metric("💡 Skills", skills_count)
            
            with col3:
                st.metric("📝 Type", resume['file_type'].upper())
            
            skills = json.loads(resume['parsed_skills']) if isinstance(resume['parsed_skills'], str) else resume['parsed_skills']
            if skills:
                st.markdown("<br>**Skills:**", unsafe_allow_html=True)
                skills_html = " ".join([f'<span class="skill-badge">{skill}</span>' for skill in skills[:15]])
                st.markdown(skills_html, unsafe_allow_html=True)
            
            if st.button(f"🗑️ Delete Resume", key=f"del_{resume['id']}", use_container_width=True):
                st.session_state.resume_repo.delete_resume(resume['id'], st.session_state.user.id)
                st.success("✅ Resume deleted!")
                st.rerun()

def show_analytics():
    """Show analytics and visualizations"""
    st.markdown('<div class="section-header">📊 Your Analytics Dashboard</div>', unsafe_allow_html=True)
    
    analyses = st.session_state.resume_repo.get_user_analyses(st.session_state.user.id, limit=50)
    
    if not analyses:
        st.markdown('<div class="info-box">📊 No analyses yet. Complete your first resume analysis to see insights!</div>', unsafe_allow_html=True)
        return
    
    df = pd.DataFrame(analyses)
    df['analysis_date'] = pd.to_datetime(df['analysis_date'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📈 Match Score Progress**")
        fig = px.line(
            df,
            x='analysis_date',
            y='match_score',
            title='Your Improvement Over Time',
            labels={'match_score': 'Match Score (%)', 'analysis_date': 'Date'}
        )
        fig.update_traces(line_color='#667eea', line_width=3)
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Poppins")
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**🎯 Roles Analyzed**")
        role_counts = df['target_role'].value_counts()
        fig = px.pie(
            values=role_counts.values,
            names=role_counts.index,
            title='Distribution of Analyzed Roles'
        )
        fig.update_traces(marker=dict(colors=px.colors.sequential.Purples))
        fig.update_layout(
            paper_bgcolor='white',
            font=dict(family="Poppins")
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<br>**🏆 Top Performing Analyses**", unsafe_allow_html=True)
    top_analyses = df.nlargest(5, 'match_score')[['target_role', 'match_score', 'analysis_date']]
    top_analyses['analysis_date'] = top_analyses['analysis_date'].dt.strftime('%Y-%m-%d')
    top_analyses.columns = ['Role', 'Match Score (%)', 'Date']
    st.dataframe(top_analyses, use_container_width=True, hide_index=True)

def main():
    """Main application logic"""
    init_session_state()

    if not st.session_state.authenticated:
        show_auth_page()
    else:
        show_dashboard()

if __name__ == "__main__":
    main()