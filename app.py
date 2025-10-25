import streamlit as st
import pandas as pd
from rapidfuzz import fuzz
from utils import extract_text_from_pdf, render_resume_pdf
from web_scraper import get_latest_skills
import streamlit.components.v1 as components
from dotenv import load_dotenv
import os
import google.generativeai as genai

# ---------------- Load Environment and Configure Gemini ----------------
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
else:
    st.warning("⚠️ Gemini API key not found. Please add it to your .env file.")

# ---------------- Page Setup ----------------
st.set_page_config("Resume Builder & Skill Analyzer", layout="wide", page_icon="📄")

# ---------------- Sidebar ----------------
st.sidebar.title("⚙️ Settings")
domain = st.sidebar.selectbox("Choose Domain", [
    "Web Development", "Data Science", "Machine Learning",
    "Android Development", "DevOps", "Software Engineering"
])
threshold = st.sidebar.slider("Skill Match Sensitivity (%)", 60, 100, 80, step=5)
show_tips = st.sidebar.checkbox("💡 Show Resume Improvement Tips (AI)", value=True)

# Fetch live skills
with st.spinner("Fetching latest skills..."):
    live_skills = get_latest_skills(domain)

st.sidebar.markdown("### 📌 Trending Skills")
st.sidebar.markdown(" ".join([
    f"<span style='background-color:#e1ecf4; color:#0366d6; padding:4px 10px; border-radius:12px; margin:2px'>{s}</span>"
    for s in live_skills
]), unsafe_allow_html=True)

# ---------------- Tabs ----------------
tab = st.sidebar.radio("Go To", ["🧠 Skill Analyzer", "📄 Resume Builder"])

# ---------------- Helper Functions ----------------
def fuzzy_match(skill, text, threshold=80):
    return fuzz.partial_ratio(skill.lower(), text.lower()) >= threshold

def match_resume_with_skills(text, skill_list, threshold=80):
    matched = [s for s in skill_list if fuzzy_match(s, text, threshold)]
    missing = [s for s in skill_list if s not in matched]
    return matched, missing

def calculate_score(matched, total_skills):
    return round((len(matched)/len(total_skills))*100,2) if total_skills else 0

def ai_suggestions(missing_skills, domain):
    """Use Gemini to suggest how to improve resume for missing skills."""
    if not missing_skills:
        return "Your resume already covers all trending skills for this domain! 🎉"
    prompt = f"""
    You are a professional career advisor.
    Suggest resume improvements for the {domain} domain.
    The user is missing the following skills: {', '.join(missing_skills)}.
    Provide short, bullet-point suggestions on how to gain or represent these skills effectively.
    """
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ AI Suggestion Error: {str(e)}"

def enhance_experience_with_ai(experience_text):
    """Enhance user’s experience lines using Gemini AI."""
    if not experience_text.strip():
        return ""
    prompt = f"Improve the following resume experience section to make it more professional:\n\n{experience_text}"
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return experience_text + f"\n\n⚠️ AI Enhancement Error: {str(e)}"

# ---------------- Skill Analyzer ----------------
if tab == "🧠 Skill Analyzer":
    st.title("🧠 Resume Skill Analyzer")
    uploaded_resume = st.file_uploader("Upload Your Resume (PDF or TXT)", type=["pdf", "txt"])

    if uploaded_resume:
        if uploaded_resume.type == "application/pdf":
            resume_text = extract_text_from_pdf(uploaded_resume)
        else:
            resume_text = uploaded_resume.read().decode("utf-8")

        matched, missing = match_resume_with_skills(resume_text, live_skills, threshold)
        score = calculate_score(matched, live_skills)

        st.metric("ATS Score", f"{score}%")
        st.markdown("### ✅ Matched Skills")
        st.markdown(" ".join([
            f"<span style='background-color:#d1fae5; color:#065f46; padding:4px 8px; border-radius:12px; margin:2px'>{s}</span>"
            for s in matched
        ]), unsafe_allow_html=True)

        st.markdown("### ⚠️ Missing Skills")
        st.markdown(" ".join([
            f"<span style='background-color:#fee2e2; color:#991b1b; padding:4px 8px; border-radius:12px; margin:2px'>{s}</span>"
            for s in missing
        ]), unsafe_allow_html=True)

        if show_tips:
            with st.expander("💡 AI-Based Suggestions"):
                ai_feedback = ai_suggestions(missing, domain)
                st.markdown(ai_feedback)

# ---------------- Resume Builder ----------------
elif tab == "📄 Resume Builder":
    st.title("📄 ATS Resume Builder")
    left_col, right_col = st.columns([1,1.2])

    with left_col:
        with st.form("resume_form"):
            st.subheader("👤 Personal Info")
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone")

            st.subheader("📝 Professional Summary")
            summary = st.text_area("Summary")

            st.subheader("💡 Skills")
            skills = st.text_area("Skills (comma separated)")

            st.subheader("🎓 Education")
            education = st.text_area("Education (one per line)")

            st.subheader("💼 Experience")
            experience = st.text_area("Experience (one per line)")

            st.subheader("🛠 Projects")
            projects = st.text_area("Projects (one per line)")

            st.subheader("🎨 Template & AI Enhancer")
            template_choice = st.selectbox("Choose Resume Template", ["ats", "modern", "creative"])
            enhance = st.checkbox("✨ Enhance Experience with AI")

            submitted = st.form_submit_button("Generate Resume")

    if submitted:
        exp_text = enhance_experience_with_ai(experience) if enhance else experience
        resume_data = {
            "name": name,
            "email": email,
            "phone": phone,
            "summary": summary,
            "skills": [s.strip() for s in skills.split(",") if s.strip()],
            "education": [e.strip() for e in education.splitlines() if e.strip()],
            "experience": [e.strip() for e in exp_text.splitlines() if e.strip()],
            "projects": [p.strip() for p in projects.splitlines() if p.strip()]
        }

        # Preview HTML in right column
        with right_col:
            st.subheader("📄 Resume Preview")
            html_preview = render_resume_pdf(resume_data, template_choice, preview=True)
            components.html(html_preview, height=800, scrolling=True)

            # Download PDF
            pdf_bytes = render_resume_pdf(resume_data, template_choice, preview=False)
            st.download_button(
                "📥 Download PDF Resume",
                pdf_bytes,
                file_name=f"{name.replace(' ','_')}_resume.pdf",
                mime="application/pdf"
            )
