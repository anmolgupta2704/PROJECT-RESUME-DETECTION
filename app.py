import streamlit as st
import pandas as pd
from rapidfuzz import fuzz
from utils import extract_text_from_pdf, render_resume_pdf
from web_scraper import get_latest_skills
import streamlit.components.v1 as components
from dotenv import load_dotenv
from google import genai
import os

# ---------------- Load Environment & Gemini Setup ----------------
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("⚠️ GOOGLE_API_KEY not found in .env file")
else:
    client = genai.Client(api_key=api_key)

# ---------------- Page Configuration ----------------
st.set_page_config(
    page_title="Resume Builder & Skill Analyzer",
    layout="wide",
    page_icon="📄"
)

# ---------------- Sidebar Settings ----------------
st.sidebar.title("⚙️ Settings")

domain = st.sidebar.selectbox(
    "Choose Domain",
    [
        "Web Development", "Data Science", "Machine Learning",
        "Android Development", "DevOps", "Software Engineering"
    ]
)

threshold = st.sidebar.slider(
    "Skill Match Sensitivity (%)", 60, 100, 80, step=5
)

show_tips = st.sidebar.checkbox("💡 Show Resume Improvement Tips (AI)", value=True)

# Fetch skills
with st.spinner("Fetching latest skills..."):
    live_skills = get_latest_skills(domain)

st.sidebar.markdown("### 📌 Trending Skills")
st.sidebar.markdown(
    " ".join([
        f"<span style='background-color:#e1ecf4; color:#0366d6;"
        f"padding:4px 10px; border-radius:12px; margin:3px'>{s}</span>"
        for s in live_skills
    ]),
    unsafe_allow_html=True,
)

# ---------------- Navigation Tabs ----------------
tab = st.sidebar.radio("Go To", ["🧠 Skill Analyzer", "📄 Resume Builder"])

# ---------------- Helper Functions ----------------
def fuzzy_match(skill, text, threshold=80):
    return fuzz.partial_ratio(skill.lower(), text.lower()) >= threshold

def match_resume_with_skills(text, skills, threshold=80):
    matched = [s for s in skills if fuzzy_match(s, text, threshold)]
    missing = [s for s in skills if s not in matched]
    return matched, missing

def calculate_score(matched, total):
    return round((len(matched) / len(total)) * 100, 2) if total else 0

def ai_suggestions(missing_skills, domain):
    if not missing_skills:
        return "🎉 Your resume already covers all important skills!"

    prompt = f"""
    You are a resume expert. The user is applying for {domain}.
    Their resume is missing these skills: {', '.join(missing_skills)}.

    Provide 5 short bullet points on:
    - Resume improvements
    - How to learn these skills
    - Projects to prove these skills
    """

    try:
        response = client.models.generate_content(
            model="models/gemini-flash-latest",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"⚠️ AI Suggestion Error: {str(e)}"


# ---------------- AI Enhance Experience ----------------
def enhance_experience_with_ai(experience_text):
    if not experience_text.strip():
        return ""

    prompt = f"""
    Rewrite the following resume experience to make it professional, ATS-optimized,
    bullet-point based, and action-driven:

    {experience_text}
    """

    try:
        response = client.models.generate_content(
            model="models/gemini-flash-latest",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"⚠️ AI Enhancement Error: {str(e)}"

# ---------------- Skill Analyzer Page ----------------
if tab == "🧠 Skill Analyzer":
    st.title("🧠 Resume Skill Analyzer")

    uploaded = st.file_uploader("Upload Your Resume", type=["pdf", "txt"])

    if uploaded:
        # Extract text
        resume_text = (
            extract_text_from_pdf(uploaded)
            if uploaded.type == "application/pdf"
            else uploaded.read().decode("utf-8")
        )

        matched, missing = match_resume_with_skills(resume_text, live_skills, threshold)
        score = calculate_score(matched, live_skills)

        st.metric("ATS Skill Score", f"{score}%")

        st.markdown("### ✅ Matched Skills")
        st.markdown(
            " ".join([
                f"<span style='background-color:#d1fae5; color:#065f46;"
                f"padding:4px 8px; border-radius:12px; margin:3px'>{s}</span>"
                for s in matched
            ]),
            unsafe_allow_html=True
        )

        st.markdown("### ⚠️ Missing Skills")
        st.markdown(
            " ".join([
                f"<span style='background-color:#fee2e2; color:#991b1b;"
                f"padding:4px 8px; border-radius:12px; margin:3px'>{s}</span>"
                for s in missing
            ]),
            unsafe_allow_html=True
        )

        if show_tips:
            with st.expander("💡 AI-Based Resume Improvement Tips"):
                st.markdown(ai_suggestions(missing, domain))

# ---------------- Resume Builder Page ----------------
elif tab == "📄 Resume Builder":
    st.title("📄 ATS Resume Builder")

    left, right = st.columns([1, 1.2])

    with left:
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

            st.subheader("✨ AI Enhancer")
            enhance = st.checkbox("Enhance Experience with AI")

            template_choice = st.selectbox("Choose Template", ["ats", "modern", "creative"])

            submitted = st.form_submit_button("Generate Resume")

    if submitted:
        exp_text = enhance_experience_with_ai(experience) if enhance else experience

        resume_data = {
            "name": name,
            "email": email,
            "phone": phone,
            "summary": summary,
            "skills": [s.strip() for s in skills.split(",") if s.strip()],
            "education": [e.strip() for e in education.split("\n") if e.strip()],
            "experience": [e.strip() for e in exp_text.split("\n") if e.strip()],
            "projects": [p.strip() for p in projects.split("\n") if p.strip()],
        }

        with right:
            st.subheader("📄 Resume Preview")
            html_preview = render_resume_pdf(resume_data, template_choice, preview=True)
            components.html(html_preview, height=800, scrolling=True)

            pdf_bytes = render_resume_pdf(resume_data, template_choice, preview=False)
            st.download_button(
                "📥 Download PDF",
                pdf_bytes,
                file_name=f"{name.replace(' ','_')}_resume.pdf",
                mime="application/pdf",
            )
