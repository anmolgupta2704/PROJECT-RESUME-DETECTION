import streamlit as st
import pandas as pd
from web_scraper import get_latest_skills
from utils import extract_text_from_pdf
from rapidfuzz import fuzz

# --- Skill Matching ---
def fuzzy_match(skill, text, threshold=80):
    return fuzz.partial_ratio(skill.lower(), text.lower()) >= threshold

def match_resume_with_skills(text, skill_list):
    matched = [s for s in skill_list if fuzzy_match(s, text)]
    missing = [s for s in skill_list if s not in matched]
    return matched, missing

def calculate_score(matched, total_skills):
    total = len(total_skills)
    return round((len(matched) / total) * 100, 2) if total > 0 else 0

# --- UI Start ---
st.set_page_config(page_title="Live Resume Skill Analyzer", layout="wide")

st.markdown("<h1 style='text-align: center;'>🌐 Live Resume Analyzer with Web Skill Integration</h1>", unsafe_allow_html=True)

domain = st.selectbox("🎯 Select Your Domain", [
    "Web Development", "Data Science", "Machine Learning", "Android Development", "DevOps", "Software Engineering"
])

if domain:
    with st.spinner("🔍 Fetching latest skills from the web..."):
        live_skills = get_latest_skills(domain)

    if live_skills:
        st.markdown("### 📌 Latest In-Demand Skills:")
        st.markdown(" ".join([f"`{s}`" for s in live_skills]))
    else:
        st.warning("❌ Could not fetch skills. Try again later.")
        st.stop()

    uploaded_resume = st.file_uploader("📁 Upload Your Resume (PDF or TXT)", type=["pdf", "txt"])

    if uploaded_resume:
        # Extract resume text
        if uploaded_resume.type == "application/pdf":
            resume_text = extract_text_from_pdf(uploaded_resume)
        else:
            resume_text = uploaded_resume.read().decode("utf-8")

        matched, missing = match_resume_with_skills(resume_text, live_skills)
        score = calculate_score(matched, live_skills)

        # Display Result
        st.markdown(f"### 📊 ATS Score: `{score}%`")
        st.progress(score / 100)

        st.markdown("### ✅ Matched Skills")
        st.markdown(" ".join([f"`{s}`" for s in matched]) or "❌ None")

        st.markdown("### ⚠️ Missing / Suggested Skills")
        st.markdown(" ".join([f"`{s}`" for s in missing]) or "🎯 Great! All skills matched.")

        # Report Download
        df = pd.DataFrame([{
            "Filename": uploaded_resume.name,
            "Domain": domain,
            "ATS Score": score,
            "Matched Skills": ", ".join(matched),
            "Missing Skills": ", ".join(missing),
        }])
        csv = df.to_csv(index=False)
        st.download_button("📥 Download Report", csv, file_name="ats_resume_report.csv", mime="text/csv")
