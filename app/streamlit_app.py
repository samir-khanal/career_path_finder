# app/streamlit_app.py
from __future__ import annotations
from pathlib import Path
import sys
import time
import streamlit as st

# Make sure we can import src/*
PROJ_ROOT = Path(__file__).resolve().parents[1]
if str(PROJ_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJ_ROOT))

try:
    from src.parsing.ml.skill_matcher import analyze_resume, load_skill_dataset, MODEL_PATH, VECT_PATH
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

UPLOADS_DIR = PROJ_ROOT / "app" / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="Resume Analyzer (Skills & Gaps)", page_icon="🧭", layout="wide")
st.title("🧭 Resume Analyzer — Skills & Gap Detection")
st.caption("Upload your PDF/DOCX resume. We'll parse, predict roles, and show your skill gaps.")

# Sidebar: Model status
with st.sidebar:
    st.header("Model")
    has_model = MODEL_PATH.exists() and VECT_PATH.exists()
    st.write(f"Status: {'✅ Found trained model' if has_model else '⚠️ Using rule-based matching'}")
    
    st.header("Skill Dataset")
    st.caption("Using comprehensive skill matching.")

# Upload
uploaded = st.file_uploader("Upload your resume", type=["pdf", "docx"])
if uploaded:
    ts = time.strftime("%Y%m%d-%H%M%S")
    safe_name = uploaded.name.replace(" ", "_")
    saved_path = UPLOADS_DIR / f"{ts}__{safe_name}"
    with saved_path.open("wb") as f:
        f.write(uploaded.getbuffer())
    st.success(f"Uploaded: {uploaded.name}")

    with st.spinner("Parsing & analyzing…"):
        roles_map = load_skill_dataset()
        result = analyze_resume(str(saved_path))

    # Left/Right columns
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🧩 Parsed Resume")
        skills = result["parsed"].get("skills", [])
        edu = result["parsed"].get("education", [])
        exp = result["parsed"].get("experience", [])
        
        st.write("**Skills:**")
        if skills:
            for skill in sorted(skills):
                st.write(f"- {skill.title()}")
        else:
            st.write("—")
            
        st.write("**Education:**")
        if edu:
            for e in edu:
                st.write(f"- {e.title()}")
        else:
            st.write("—")
            
        st.write("**Experience:**")
        if exp:
            for e in exp:
                st.write(f"- {e.title()}")
        else:
            st.write("—")

    with col2:
        st.subheader("🎯 Role Prediction")
        preds = result.get("predictions", [])
        if preds:
            for role, score in preds:
                st.write(f"- **{role}** — {score:.1f}%")
            default_role = preds[0][0]
        else:
            st.info("No role predictions available.")
            default_role = result["chosen_role"]

        chosen = st.selectbox(
            "Target role for gap analysis",
            options=list(roles_map.keys()),
            index=list(roles_map.keys()).index(default_role) if default_role in roles_map else 0
        )

        # Recompute gap for the chosen role
        if chosen != result["chosen_role"]:
            with st.spinner("Recalculating for selected role..."):
                result = analyze_resume(str(saved_path), chosen_role=chosen)

        st.markdown("### ✅ Matched Skills")
        matched = result["gap"].get("matched", [])
        if matched:
            for skill in sorted(matched):
                st.write(f"- {skill.title()}")
        else:
            st.write("—")

        st.markdown("### ❌ Missing Skills")
        missing = result["gap"].get("missing", [])
        if missing:
            for skill in sorted(missing):
                st.write(f"- {skill.title()}")
        else:
            st.success("Great! No core skills missing.")

        st.metric("Match Score", f"{result.get('match_score', 0):.1f}%")

    # Clean up
    if saved_path.exists():
        saved_path.unlink()