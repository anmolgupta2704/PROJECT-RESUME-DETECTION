import streamlit as st
import pandas as pd
from web_scraper import get_latest_skills
from utils import extract_text_from_pdf
from rapidfuzz import fuzz
import datetime

# --- Skill Matching Logic ---
def fuzzy_match(skill, text, threshold=80):
    return fuzz.partial_ratio(skill.lower(), text.lower()) >= threshold

def match_resume_with_skills(text, skill_list, threshold=80):
    matched = [s for s in skill_list if fuzzy_match(s, text, threshold)]
    missing = [s for s in skill_list if s not in matched]
    return matched, missing

def calculate_score(matched, total_skills):
    total = len(total_skills)
    return round((len(matched) / total) * 100, 2) if total > 0 else 0

# --- Page Setup ---
st.set_page_config("Live Resume Skill Analyzer", layout="wide")

st.markdown("""
    <style>
        .center { text-align: center; }
        .skill-badge {
            display: inline-block;
            background-color: #e1ecf4;
            border-radius: 15px;
            padding: 6px 12px;
            margin: 4px;
            font-size: 0.85em;
            color: #0366d6;
            border: 1px solid #0366d6;
        }
        .stDownloadButton > button {
            background-color: #4CAF50;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("<h1 class='center'>🧠 Live Resume Skill Analyzer</h1>", unsafe_allow_html=True)
st.markdown("<p class='center'>Match your resume with trending skills and improve your chances!</p>", unsafe_allow_html=True)
st.markdown("---")

# --- Sidebar ---
st.sidebar.title("⚙️ Settings")
domain = st.sidebar.selectbox("Choose Domain", [
    "Web Development", "Data Science", "Machine Learning", "Android Development", "DevOps", "Software Engineering"
])
threshold = st.sidebar.slider("Skill Match Sensitivity (%)", 60, 100, 80, step=5)
show_tips = st.sidebar.checkbox("💡 Show Resume Improvement Tips", value=True)

# --- Skill Fetching ---
with st.spinner("🔍 Fetching latest skills..."):
    live_skills = get_latest_skills(domain)

if not live_skills:
    st.error("❌ Could not retrieve skills. Please try again.")
    st.stop()

st.markdown("### 📌 Trending Skills in This Domain:")
st.markdown(" ".join([f"<span class='skill-badge'>{s}</span>" for s in live_skills]), unsafe_allow_html=True)

# --- File Upload ---
uploaded_resume = st.file_uploader("📄 Upload Your Resume (PDF or TXT)", type=["pdf", "txt"])

if uploaded_resume:
    if uploaded_resume.type == "application/pdf":
        resume_text = extract_text_from_pdf(uploaded_resume)
    else:
        resume_text = uploaded_resume.read().decode("utf-8")

    matched, missing = match_resume_with_skills(resume_text, live_skills, threshold)
    score = calculate_score(matched, live_skills)

    st.markdown("---")
    st.subheader("📊 Resume Analysis")

    col1, col2, col3 = st.columns(3)
    col1.metric("Matched Skills", len(matched))
    col2.metric("Missing Skills", len(missing))
    col3.metric("ATS Score", f"{score}%")
    st.progress(score / 100)

    st.markdown("#### ✅ Skills Found in Resume")
    st.markdown(" ".join([f"<span class='skill-badge'>{s}</span>" for s in matched]) or "❌ None", unsafe_allow_html=True)

    st.markdown("#### ⚠️ Skills Missing or Recommended")
    st.markdown(" ".join([f"<span class='skill-badge'>{s}</span>" for s in missing]) or "🎯 All skills matched!", unsafe_allow_html=True)

    # --- Tips ---
    if show_tips and missing:
        st.markdown("### 💡 Resume Improvement Suggestions")
        for s in missing:
            st.markdown(f"- Add relevant experience with **{s}** if possible.")

    # --- Download Report ---
    df = pd.DataFrame([{
        "Filename": uploaded_resume.name,
        "Domain": domain,
        "ATS Score": score,
        "Matched Skills": ", ".join(matched),
        "Missing Skills": ", ".join(missing),
        "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }])
    csv = df.to_csv(index=False)

    st.markdown("### 📥 Download Reports")
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("📄 Full CSV Report", csv, file_name="ATS_Report.csv", mime="text/csv")
    with col2:
        st.download_button("✅ Matched Skills Only", "\n".join(matched), file_name="matched_skills.txt", mime="text/plain")

    st.markdown("---")
    if st.button("🔄 Clear Resume"):
        st.rerun()
