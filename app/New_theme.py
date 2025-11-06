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

st.set_page_config(
    page_title="AI Resume Analyzer Pro",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ✅ MINIMALIST WHITE PREMIUM UI - Inspired by Image Examples
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * {
        font-family: 'Inter', sans-serif;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main app background - Clean White */
    .stApp {
        background: #ffffff;
    }

    /* ============================================
       LOGIN PAGE STYLING - Minimalist Design
    ============================================ */
    .login-container {
        max-width: 400px;
        margin: 80px auto;
        background: white;
        border-radius: 12px;
        padding: 40px;
        box-shadow: 0 2px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid #e5e5e5;
    }

    .login-header {
        text-align: center;
        margin-bottom: 32px;
    }

    .login-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #000000;
        margin-bottom: 8px;
    }

    .login-subtitle {
        color: #666;
        font-size: 0.9rem;
        font-weight: 400;
    }

    /* ============================================
       DASHBOARD STYLING - Clean Professional
    ============================================ */
    .dashboard-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 20px;
    }

    /* Header */
    .dashboard-header {
        background: white;
        padding: 24px 0;
        margin: 0 0 30px 0;
        border-bottom: 1px solid #e5e5e5;
    }

    .welcome-section {
        background: #f8f9fa;
        padding: 24px;
        border-radius: 8px;
        margin-bottom: 32px;
        border-left: 4px solid #000000;
    }

    .welcome-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #000000;
        margin: 0 0 8px 0;
    }

    .welcome-subtitle {
        color: #666;
        font-size: 0.95rem;
        margin: 0;
    }

    /* Stats Grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 32px;
    }

    .stat-card {
        background: white;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #e5e5e5;
        text-align: center;
    }

    .stat-number {
        font-size: 1.8rem;
        font-weight: 600;
        color: #000000;
        margin: 8px 0;
    }

    .stat-label {
        font-size: 0.8rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 500;
    }

    /* Section Headers */
    .section-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #000000;
        margin: 32px 0 20px 0;
        padding-bottom: 12px;
        border-bottom: 1px solid #e5e5e5;
    }

    /* Buttons - Clean Black Style */
    .stButton > button {
        background: #000000;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 12px 24px;
        font-weight: 500;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        width: 100%;
    }

    .stButton > button:hover {
        background: #333333;
        transform: translateY(-1px);
    }

    /* Secondary Button */
    .secondary-btn button {
        background: white !important;
        color: #000000 !important;
        border: 1px solid #e5e5e5 !important;
    }

    .secondary-btn button:hover {
        background: #f8f9fa !important;
        border-color: #000000 !important;
    }

    /* Tabs - Minimal */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background: #f8f9fa;
        padding: 4px;
        border-radius: 6px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 42px;
        background: transparent;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: 500;
        color: #666;
        border: none;
    }

    .stTabs [aria-selected="true"] {
        background: white;
        color: #000000;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }

    /* Input Fields */
    .stTextInput > div > div > input {
        border-radius: 6px;
        border: 1px solid #e5e5e5;
        padding: 12px 16px;
        font-size: 0.95rem;
    }

    .stTextInput > div > div > input:focus {
        border-color: #000000;
        box-shadow: 0 0 0 1px #000000;
    }

    /* File Uploader */
    .uploadedFile {
        background: #f8f9fa;
        border: 1px dashed #d1d5db;
        border-radius: 6px;
        padding: 20px;
    }

    /* Skill Badges */
    .skill-badge {
        display: inline-block;
        background: #f8f9fa;
        color: #000000;
        padding: 6px 12px;
        border-radius: 16px;
        margin: 4px;
        font-weight: 500;
        font-size: 0.8rem;
        border: 1px solid #e5e5e5;
    }

    .skill-badge-missing {
        background: #fee2e2;
        color: #dc2626;
        border-color: #fecaca;
    }

    /* Message Boxes */
    .success-box {
        background: #f0f9f4;
        padding: 16px 20px;
        border-radius: 6px;
        color: #065f46;
        margin: 16px 0;
        font-weight: 500;
        border-left: 4px solid #10b981;
    }

    .warning-box {
        background: #fffbeb;
        padding: 16px 20px;
        border-radius: 6px;
        color: #92400e;
        margin: 16px 0;
        font-weight: 500;
        border-left: 4px solid #f59e0b;
    }

    .info-box {
        background: #eff6ff;
        padding: 16px 20px;
        border-radius: 6px;
        color: #1e40af;
        margin: 16px 0;
        font-weight: 500;
        border-left: 4px solid #3b82f6;
    }

    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: #000000;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: #f8f9fa;
        border-radius: 6px;
        font-weight: 500;
        color: #000000;
        border: 1px solid #e5e5e5;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.4rem;
        font-weight: 600;
        color: #000000;
    }

    [data-testid="stMetricLabel"] {
        color: #666;
        font-weight: 500;
    }

    /* Remove padding */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
    }

    /* Selectbox */
    .stSelectbox > div > div {
        border-radius: 6px;
        border: 1px solid #e5e5e5;
    }

    /* Footer */
    .footer {
        background: #f8f9fa;
        padding: 40px 0;
        margin-top: 60px;
        border-top: 1px solid #e5e5e5;
    }

    .footer-content {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 20px;
    }

    .footer-section {
        margin-bottom: 20px;
    }

    .footer-title {
        font-weight: 600;
        color: #000000;
        margin-bottom: 12px;
        font-size: 0.95rem;
    }

    .footer-link {
        display: block;
        color: #666;
        text-decoration: none;
        margin-bottom: 8px;
        font-size: 0.9rem;
        transition: color 0.2s ease;
    }

    .footer-link:hover {
        color: #000000;
    }

    .footer-bottom {
        text-align: center;
        padding-top: 20px;
        border-top: 1px solid #e5e5e5;
        color: #666;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

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

def show_auth_page():
    """Show minimalist authentication page"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="login-container">
            <div class="login-header">
                <div class="login-title">AI Resume Analyzer Pro</div>
                <div class="login-subtitle">Advanced Resume Analysis & Skill Gap Detection</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
        
        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("signin_form", clear_on_submit=False):
                email = st.text_input("Email Address", placeholder="your.email@example.com", key="signin_email")
                password = st.text_input("Password", type="password", placeholder="Enter your password", key="signin_password")
                
                st.markdown("<br>", unsafe_allow_html=True)
                submit = st.form_submit_button("Sign In", use_container_width=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown('<div style="font-size: 0.85rem; color: #666;">Forgot password?</div>', unsafe_allow_html=True)
                with col2:
                    st.markdown('<div style="font-size: 0.85rem; color: #666; text-align: right;">New here? Create account</div>', unsafe_allow_html=True)
                
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
                full_name = st.text_input("Full Name", placeholder="John Doe", key="signup_name")
                email = st.text_input("Email Address", placeholder="your.email@example.com", key="signup_email")
                password = st.text_input("Password", type="password", placeholder="Choose a strong password", key="signup_password")
                password_confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password", key="signup_confirm")
                
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

def show_dashboard():
    """Show clean professional dashboard"""
    st.markdown('<div class="dashboard-container">', unsafe_allow_html=True)
    
    # Header
    col1, col2 = st.columns([4, 1])
    with col1:
        user_name = st.session_state.user.email.split('@')[0].title() if st.session_state.user else "User"
        st.markdown(f"""
        <div class="welcome-section">
            <div class="welcome-title">Welcome back, {user_name}!</div>
            <div class="welcome-subtitle">Track your resume analysis, match scores, and skill development journey</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
        if st.button("Sign Out", use_container_width=True):
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
            <div class="stat-label">Total Resumes</div>
            <div class="stat-number">{stats['total_resumes']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Analyses Done</div>
            <div class="stat-number">{stats['total_analyses']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Avg Match</div>
            <div class="stat-number">{stats['average_match_score']}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Unique Skills</div>
            <div class="stat-number">{stats['unique_skills']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["Upload & Analyze", "My Resumes", "Analytics"])
    
    with tab1:
        show_upload_section()
    
    with tab2:
        show_my_resumes()
    
    with tab3:
        show_analytics()
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_upload_section():
    """Upload and analyze resume section"""
    st.markdown('<div class="section-header">Upload Your Resume</div>', unsafe_allow_html=True)
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
        
        with st.spinner("Analyzing your resume with AI..."):
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
            st.markdown('<div class="section-header">Extracted Information</div>', unsafe_allow_html=True)
            
            skills = result["parsed"].get("skills", [])
            edu = result["parsed"].get("education", [])
            exp = result["parsed"].get("experience", [])
            
            st.markdown("**Skills Found:**")
            if skills:
                skills_html = " ".join([f'<span class="skill-badge">{skill.title()}</span>' 
                                       for skill in sorted(skills)[:20]])
                st.markdown(skills_html, unsafe_allow_html=True)
                if len(skills) > 20:
                    st.info(f"+ {len(skills) - 20} more skills")
            else:
                st.markdown('<div class="warning-box">⚠️ No skills detected</div>', unsafe_allow_html=True)
            
            st.markdown("<br>**Education:**")
            if edu:
                for e in edu[:3]:
                    st.write(f"• {e}")
            else:
                st.write("—")
            
            st.markdown("<br>**Experience:**")
            if exp:
                for e in exp[:3]:
                    st.write(f"• {e}")
            else:
                st.write("—")
        
        with col2:
            st.markdown('<div class="section-header">Job Role Analysis</div>', unsafe_allow_html=True)
            
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
                "Select Target Role for Detailed Analysis",
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
            st.markdown('<div class="section-header">Matched Skills</div>', unsafe_allow_html=True)
            if matched:
                matched_html = " ".join([f'<span class="skill-badge">{skill.title()}</span>' 
                                        for skill in sorted(matched)])
                st.markdown(matched_html, unsafe_allow_html=True)
            else:
                st.write("—")
        
        with col2:
            st.markdown('<div class="section-header">Skills to Learn</div>', unsafe_allow_html=True)
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
    st.markdown('<div class="section-header">Your Resume History</div>', unsafe_allow_html=True)
    
    resumes = st.session_state.resume_repo.get_user_resumes(st.session_state.user.id)
    
    if not resumes:
        st.markdown('<div class="info-box">📭 No resumes yet. Upload your first resume in the "Upload & Analyze" tab!</div>', unsafe_allow_html=True)
        return
    
    for resume in resumes:
        with st.expander(f"{resume['filename']} — {resume['upload_date'][:10]}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("File Size", f"{resume['file_size'] / 1024:.1f} KB")
            
            with col2:
                skills_count = len(json.loads(resume['parsed_skills'])) if isinstance(resume['parsed_skills'], str) else len(resume['parsed_skills'])
                st.metric("Skills", skills_count)
            
            with col3:
                st.metric("Type", resume['file_type'].upper())
            
            skills = json.loads(resume['parsed_skills']) if isinstance(resume['parsed_skills'], str) else resume['parsed_skills']
            if skills:
                st.markdown("<br>**Skills:**", unsafe_allow_html=True)
                skills_html = " ".join([f'<span class="skill-badge">{skill}</span>' for skill in skills[:15]])
                st.markdown(skills_html, unsafe_allow_html=True)
            
            if st.button(f"Delete Resume", key=f"del_{resume['id']}", use_container_width=True):
                st.session_state.resume_repo.delete_resume(resume['id'], st.session_state.user.id)
                st.success("✅ Resume deleted!")
                st.rerun()

def show_analytics():
    """Show analytics and visualizations"""
    st.markdown('<div class="section-header">Analytics Dashboard</div>', unsafe_allow_html=True)
    
    analyses = st.session_state.resume_repo.get_user_analyses(st.session_state.user.id, limit=50)
    
    if not analyses:
        st.markdown('<div class="info-box">📊 No analyses yet. Complete your first resume analysis to see insights!</div>', unsafe_allow_html=True)
        return
    
    df = pd.DataFrame(analyses)
    df['analysis_date'] = pd.to_datetime(df['analysis_date'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Match Score Progress**")
        fig = px.line(
            df,
            x='analysis_date',
            y='match_score',
            labels={'match_score': 'Match Score (%)', 'analysis_date': 'Date'}
        )
        fig.update_traces(line_color='#000000', line_width=2)
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Inter"),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**Roles Analyzed**")
        role_counts = df['target_role'].value_counts()
        fig = px.pie(
            values=role_counts.values,
            names=role_counts.index,
        )
        fig.update_traces(marker=dict(colors=['#000000', '#333333', '#666666', '#999999']))
        fig.update_layout(
            paper_bgcolor='white',
            font=dict(family="Inter"),
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<br>**Top Performing Analyses**", unsafe_allow_html=True)
    top_analyses = df.nlargest(5, 'match_score')[['target_role', 'match_score', 'analysis_date']]
    top_analyses['analysis_date'] = top_analyses['analysis_date'].dt.strftime('%Y-%m-%d')
    top_analyses.columns = ['Role', 'Match Score (%)', 'Date']
    st.dataframe(top_analyses, use_container_width=True, hide_index=True)

def show_footer():
    """Show minimalist footer"""
    st.markdown("""
    <div class="footer">
        <div class="footer-content">
            <div class="footer-section">
                <div class="footer-title">Services</div>
                <a href="#" class="footer-link">AI Resume Analysis</a>
                <a href="#" class="footer-link">Skill Gap Detection</a>
                <a href="#" class="footer-link">Career Path Planning</a>
            </div>
            
            <div class="footer-section">
                <div class="footer-title">How to Use</div>
                <a href="#" class="footer-link">Quick Start Guide</a>
                <a href="#" class="footer-link">FAQ</a>
                <a href="#" class="footer-link">Support</a>
            </div>
            
            <div class="footer-section">
                <div class="footer-title">Company</div>
                <a href="#" class="footer-link">About</a>
                <a href="#" class="footer-link">Privacy Policy</a>
                <a href="#" class="footer-link">Terms of Service</a>
            </div>
            
            <div class="footer-section">
                <div class="footer-title">Social</div>
                <a href="#" class="footer-link">Twitter / X</a>
                <a href="#" class="footer-link">LinkedIn</a>
                <a href="#" class="footer-link">GitHub</a>
            </div>
            
            <div class="footer-bottom">
                © 2024 AI Resume Analyzer Pro — All rights reserved.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application logic"""
    init_session_state()

    if not st.session_state.authenticated:
        show_auth_page()
    else:
        show_dashboard()
    
    show_footer()

if __name__ == "__main__":
    main()