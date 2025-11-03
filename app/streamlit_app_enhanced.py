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
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ✅ MODERN PROFESSIONAL UI - Like Popular Websites
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
    }

    /* ============================================
       LOGIN PAGE STYLING - Modern Card Design
    ============================================ */
    .login-container {
        max-width: 450px;
        margin: 60px auto;
        background: white;
        border-radius: 20px;
        padding: 40px;
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
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
    }

    .login-subtitle {
        color: #666;
        font-size: 0.95rem;
        font-weight: 400;
    }

    /* ============================================
       DASHBOARD STYLING - Modern Layout
    ============================================ */
    .dashboard-header {
        background: white;
        padding: 20px 40px;
        margin: -70px -70px 30px -70px;
        border-bottom: 1px solid #e5e7eb;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .dashboard-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1f2937;
        margin: 0;
    }

    .dashboard-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 40px;
        background: rgba(255, 255, 255, 0.98);
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
        margin-top: 20px;
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
        font-size: 1.8rem;
        font-weight: 600;
        color: white !important;
        border: none !important;
        padding: 0 !important;
    }

    .welcome-banner p {
        margin: 0;
        opacity: 0.95;
        font-size: 1rem;
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
        padding: 25px;
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
        font-size: 2.5rem;
        font-weight: 800;
        margin: 10px 0;
    }

    .stat-label {
        font-size: 0.85rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 500;
    }

    /* Section Headers */
    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #1f2937;
        margin: 30px 0 20px 0;
        padding-bottom: 10px;
        border-bottom: 2px solid #e5e7eb;
    }

    /* Buttons - Modern Style */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 30px;
        font-weight: 600;
        font-size: 1rem;
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
        padding: 8px;
        border-radius: 12px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background: transparent;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
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
        padding: 12px 16px;
        font-size: 1rem;
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
        padding: 20px;
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
        padding: 8px 16px;
        border-radius: 20px;
        margin: 5px;
        font-weight: 600;
        font-size: 0.85rem;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }

    .skill-badge-missing {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    }

    /* Message Boxes */
    .success-box {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        padding: 16px 20px;
        border-radius: 12px;
        color: white;
        margin: 15px 0;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }

    .warning-box {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        padding: 16px 20px;
        border-radius: 12px;
        color: white;
        margin: 15px 0;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
    }

    .info-box {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        padding: 16px 20px;
        border-radius: 12px;
        color: white;
        margin: 15px 0;
        font-weight: 500;
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
        color: #374151;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
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
        padding: 25px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }

    /* Selectbox */
    .stSelectbox > div > div {
        border-radius: 10px;
        border: 2px solid #e5e7eb;
    }

    /* Sign out button */
    .sign-out-btn button {
        background: white !important;
        color: #667eea !important;
        border: 2px solid #667eea !important;
        padding: 8px 20px !important;
        font-size: 0.9rem !important;
    }

    .sign-out-btn button:hover {
        background: #667eea !important;
        color: white !important;
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
    """Show modern authentication page"""
    # Center the login card
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="login-container">
            <div class="login-header">
                <div class="login-title"> AI Resume Analyzer Pro</div>
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

# ============================================
# 🌐 CUSTOM FOOTER SECTION (Modern Gradient)
# ============================================
def show_footer():
    st.markdown("""
    <style>
        .footer {
            position: relative;
            bottom: 0;
            width: 100%;
            text-align: center;
            padding: 25px 0;
            margin-top: 60px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-top-left-radius: 20px;
            border-top-right-radius: 20px;
            box-shadow: 0 -5px 20px rgba(0,0,0,0.1);
        }
        .footer a {
            color: white;
            text-decoration: none;
            font-weight: 600;
            margin: 0 12px;
            transition: color 0.3s ease;
        }
        .footer a:hover {
            color: #ffd700;
        }
        .footer p {
            margin: 5px 0 0 0;
            font-size: 0.95rem;
            opacity: 0.9;
        }
        .social-icons {
            margin-top: 10px;
        }
        .social-icons a {
            margin: 0 8px;
            display: inline-block;
            font-size: 1.2rem;
        }
    </style>

    <div class="footer">
        <p>🚀 Built with ❤️ by <strong>Samir Khanal, Sijan Poudel and Ishant Chalise</strong></p>
        <div class="social-icons">
            <a href="https://github.com/samir-khanal" target="_blank">💻 GitHub</a> |
            <a href="https://www.linkedin.com/in/samir-khanal7/" target="_blank">🔗 LinkedIn</a> |
        </div>
        <p>© 2025 AI Resume Analyzer Pro — All Rights Reserved.</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application logic"""
    init_session_state()

    if not st.session_state.authenticated:
        show_auth_page()
    else:
        show_dashboard()

if __name__ == "__main__":
    main()

show_footer()