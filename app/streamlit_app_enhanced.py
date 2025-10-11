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
    from src.parsing.ml.skill_matcher import analyze_resume
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
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    * {
        font-family: 'Inter', sans-serif;
    }

    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }

    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    .main-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        backdrop-filter: blur(10px);
        margin: 20px;
    }

    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem !important;
        text-align: center;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }

    h2 {
        color: #667eea;
        font-weight: 700;
        border-bottom: 3px solid #667eea;
        padding-bottom: 10px;
        margin-top: 30px;
    }

    h3 {
        color: #764ba2;
        font-weight: 600;
    }

    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 30px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }

    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 15px;
        color: white;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        text-align: center;
        transition: transform 0.3s ease;
    }

    .stat-card:hover {
        transform: translateY(-5px);
    }

    .stat-number {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 10px 0;
    }

    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .skill-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        margin: 5px;
        font-weight: 500;
        font-size: 14px;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }

    .skill-badge-missing {
        background: linear-gradient(135deg, #fc466b 0%, #3f5efb 100%);
    }

    .success-box {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin: 15px 0;
        font-weight: 500;
    }

    .warning-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin: 15px 0;
        font-weight: 500;
    }

    .info-box {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin: 15px 0;
        font-weight: 500;
    }

    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    .uploadedFile {
        background: rgba(102, 126, 234, 0.1);
        border: 2px dashed #667eea;
        border-radius: 15px;
        padding: 20px;
    }

    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        color: white;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }

    .metric-container {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 10px 0;
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
    """Show authentication page"""
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown("<h1>🎯 AI Resume Analyzer Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #666; margin-bottom: 30px;'>Advanced Resume Analysis & Skill Gap Detection</p>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔐 Sign In", "📝 Sign Up"])

    with tab1:
        with st.form("signin_form"):
            st.subheader("Welcome Back!")
            email = st.text_input("Email", placeholder="your.email@example.com")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit = st.form_submit_button("Sign In", use_container_width=True)

            if submit:
                if email and password:
                    with st.spinner("Signing in..."):
                        result = st.session_state.auth_service.sign_in(email, password)
                        if result['success']:
                            st.session_state.authenticated = True
                            st.session_state.user = result['user']
                            st.session_state.page = 'dashboard'
                            st.success(result['message'])
                            st.rerun()
                        else:
                            st.error(result['message'])
                else:
                    st.warning("Please fill in all fields")

    with tab2:
        with st.form("signup_form"):
            st.subheader("Create Account")
            full_name = st.text_input("Full Name", placeholder="John Doe")
            email = st.text_input("Email", placeholder="your.email@example.com")
            password = st.text_input("Password", type="password", placeholder="Choose a strong password")
            password_confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password")
            submit = st.form_submit_button("Sign Up", use_container_width=True)

            if submit:
                if all([full_name, email, password, password_confirm]):
                    if password == password_confirm:
                        with st.spinner("Creating account..."):
                            result = st.session_state.auth_service.sign_up(email, password, full_name)
                            if result['success']:
                                st.success(result['message'])
                                st.info("Please use the Sign In tab to access your account")
                            else:
                                st.error(result['message'])
                    else:
                        st.error("Passwords do not match!")
                else:
                    st.warning("Please fill in all fields")

    st.markdown('</div>', unsafe_allow_html=True)

def show_dashboard():
    """Show main dashboard"""
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("<h1>🎯 Resume Analyzer Dashboard</h1>", unsafe_allow_html=True)
    with col2:
        if st.button("🚪 Sign Out"):
            st.session_state.auth_service.sign_out()
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.page = 'auth'
            st.rerun()

    user_email = st.session_state.user.email if st.session_state.user else "Guest"
    st.markdown(f"<p style='text-align: center; color: #666;'>Welcome back, <strong>{user_email}</strong>!</p>", unsafe_allow_html=True)

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
            <div class="stat-label">Avg Match Score</div>
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

    st.markdown("---")

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
    st.markdown("## 📤 Upload Your Resume")

    uploaded = st.file_uploader(
        "Choose your resume file (PDF or DOCX)",
        type=["pdf", "docx"],
        help="Upload your resume for AI-powered analysis"
    )

    if uploaded:
        ts = time.strftime("%Y%m%d-%H%M%S")
        safe_name = uploaded.name.replace(" ", "_")
        saved_path = UPLOADS_DIR / f"{ts}__{safe_name}"

        with saved_path.open("wb") as f:
            f.write(uploaded.getbuffer())

        st.markdown('<div class="success-box">✅ Resume uploaded successfully!</div>', unsafe_allow_html=True)

        with st.spinner("🔍 Analyzing your resume with AI..."):
            progress = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress.progress(i + 1)

            roles_map = st.session_state.skill_repo.get_all_job_roles()
            result = analyze_resume(str(saved_path))

            raw_text = saved_path.read_text(errors='ignore') if saved_path.suffix == '.txt' else ""

            resume_record = st.session_state.resume_repo.save_resume(
                user_id=st.session_state.user.id,
                filename=uploaded.name,
                file_type=uploaded.type.split('/')[-1],
                raw_text=raw_text[:10000],
                parsed_data=result["parsed"],
                file_size=uploaded.size
            )

        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("### 🧩 Extracted Information")

            skills = result["parsed"].get("skills", [])
            edu = result["parsed"].get("education", [])
            exp = result["parsed"].get("experience", [])

            st.markdown("**💡 Skills Found:**")
            if skills:
                skills_html = " ".join([f'<span class="skill-badge">{skill.title()}</span>' for skill in sorted(skills)[:15]])
                st.markdown(skills_html, unsafe_allow_html=True)
                if len(skills) > 15:
                    st.info(f"+ {len(skills) - 15} more skills")
            else:
                st.markdown('<div class="warning-box">⚠️ No skills detected</div>', unsafe_allow_html=True)

            st.markdown("**🎓 Education:**")
            if edu:
                for e in edu[:3]:
                    st.write(f"• {e.title()}")
            else:
                st.write("—")

            st.markdown("**💼 Experience:**")
            if exp:
                for e in exp[:3]:
                    st.write(f"• {e.title()}")
            else:
                st.write("—")

        with col2:
            st.markdown("### 🎯 Job Role Predictions")

            preds = result.get("predictions", [])
            if preds:
                for role, score in preds[:5]:
                    st.markdown(f"**{role}** — {score:.1f}%")
                    st.progress(score / 100)

                default_role = preds[0][0]
            else:
                st.markdown('<div class="info-box">ℹ️ No predictions available</div>', unsafe_allow_html=True)
                default_role = list(roles_map.keys())[0] if roles_map else "Data Scientist"

            st.markdown("---")

            chosen = st.selectbox(
                "🎯 Select Target Role for Gap Analysis",
                options=list(roles_map.keys()),
                index=list(roles_map.keys()).index(default_role) if default_role in roles_map else 0
            )

            if chosen != result["chosen_role"]:
                with st.spinner("Recalculating..."):
                    result = analyze_resume(str(saved_path), chosen_role=chosen)

            matched = result["gap"].get("matched", [])
            missing = result["gap"].get("missing", [])
            match_score = result.get('match_score', 0)

            st.markdown(f"### Match Score: {match_score:.1f}%")
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

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### ✅ Matched Skills")
            if matched:
                matched_html = " ".join([f'<span class="skill-badge">{skill.title()}</span>' for skill in sorted(matched)])
                st.markdown(matched_html, unsafe_allow_html=True)
            else:
                st.write("—")

        with col2:
            st.markdown("### ❌ Missing Skills")
            if missing:
                missing_html = " ".join([f'<span class="skill-badge skill-badge-missing">{skill.title()}</span>' for skill in sorted(missing)])
                st.markdown(missing_html, unsafe_allow_html=True)
            else:
                st.markdown('<div class="success-box">🎉 Excellent! No core skills missing!</div>', unsafe_allow_html=True)

        if saved_path.exists():
            saved_path.unlink()

def show_my_resumes():
    """Show user's uploaded resumes"""
    st.markdown("## 📁 My Resume History")

    resumes = st.session_state.resume_repo.get_user_resumes(st.session_state.user.id)

    if not resumes:
        st.markdown('<div class="info-box">📭 No resumes uploaded yet. Upload your first resume in the "Upload & Analyze" tab!</div>', unsafe_allow_html=True)
        return

    for resume in resumes:
        with st.expander(f"📄 {resume['filename']} — Uploaded on {resume['upload_date'][:10]}"):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("File Size", f"{resume['file_size'] / 1024:.1f} KB")

            with col2:
                skills_count = len(json.loads(resume['parsed_skills'])) if isinstance(resume['parsed_skills'], str) else len(resume['parsed_skills'])
                st.metric("Skills Found", skills_count)

            with col3:
                st.metric("File Type", resume['file_type'].upper())

            skills = json.loads(resume['parsed_skills']) if isinstance(resume['parsed_skills'], str) else resume['parsed_skills']
            if skills:
                st.markdown("**Skills:**")
                skills_html = " ".join([f'<span class="skill-badge">{skill}</span>' for skill in skills[:10]])
                st.markdown(skills_html, unsafe_allow_html=True)

            if st.button(f"🗑️ Delete", key=f"del_{resume['id']}"):
                st.session_state.resume_repo.delete_resume(resume['id'], st.session_state.user.id)
                st.success("Resume deleted!")
                st.rerun()

def show_analytics():
    """Show analytics and visualizations"""
    st.markdown("## 📊 Your Analytics Dashboard")

    analyses = st.session_state.resume_repo.get_user_analyses(st.session_state.user.id, limit=50)

    if not analyses:
        st.markdown('<div class="info-box">📊 No analyses yet. Complete your first resume analysis to see insights!</div>', unsafe_allow_html=True)
        return

    df = pd.DataFrame(analyses)

    df['analysis_date'] = pd.to_datetime(df['analysis_date'])

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📈 Match Score Trend")
        fig = px.line(
            df,
            x='analysis_date',
            y='match_score',
            title='Your Progress Over Time',
            labels={'match_score': 'Match Score (%)', 'analysis_date': 'Date'}
        )
        fig.update_traces(line_color='#667eea', line_width=3)
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### 🎯 Target Roles Distribution")
        role_counts = df['target_role'].value_counts()
        fig = px.pie(
            values=role_counts.values,
            names=role_counts.index,
            title='Roles You\'ve Analyzed'
        )
        fig.update_traces(marker=dict(colors=px.colors.sequential.Purples))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🏆 Top Performing Analyses")
    top_analyses = df.nlargest(5, 'match_score')[['target_role', 'match_score', 'analysis_date']]
    top_analyses['analysis_date'] = top_analyses['analysis_date'].dt.strftime('%Y-%m-%d')
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
