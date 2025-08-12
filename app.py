import streamlit as st
import pandas as pd
from rapidfuzz import fuzz
from utils import extract_text_from_pdf

# ----------------- Skill Sets -------------------
domain_skills = {
    "Web Development": {
        "HTML": 2, "CSS": 2, "JavaScript": 3, "React": 3, "Node.js": 2, "Git": 1, "Bootstrap": 1,
    },
    "Android Development": {
        "Java": 3, "Kotlin": 3, "Android Studio": 3, "XML": 1, "Firebase": 2,
    },
    "Data Science": {
        "Python": 3, "Pandas": 3, "NumPy": 3, "Scikit-learn": 3, "Matplotlib": 2, "Jupyter": 1, "SQL": 2,
    },
    "Machine Learning": {
        "TensorFlow": 3, "PyTorch": 3, "Scikit-learn": 3, "ML algorithms": 3, "Python": 3,
    },
    "DevOps": {
        "Docker": 3, "Kubernetes": 3, "AWS": 3, "Azure": 3, "CI/CD": 3, "Linux": 2,
    },
    "Software Engineering": {
        "Java": 3, "C++": 3, "Python": 3, "Git": 2, "OOP": 3, "Data Structures": 3, "Algorithms": 3,
    },
}

# ----------------- Synonyms -------------------
skill_synonyms = {
    "JavaScript": ["js", "javascript", "java script"],
    "React": ["reactjs", "react.js", "react"],
    "Git": ["git", "github", "gitlab"],
    "SQL": ["sql", "structured query language"],
    "Python": ["python"],
}

# ----------------- Matching Logic -------------------
def fuzzy_skill_match(text, skill, threshold=80):
    candidates = skill_synonyms.get(skill, [skill])
    for candidate in candidates:
        if fuzz.partial_ratio(candidate.lower(), text.lower()) >= threshold:
            return True
    return False

def detect_domain(text):
    scores = {}
    for domain, skills in domain_skills.items():
        matched_weight = sum(
            weight for skill, weight in skills.items() if fuzzy_skill_match(text, skill)
        )
        scores[domain] = matched_weight
    best = max(scores, key=scores.get)
    return best, scores[best]

def get_matched_and_missing(text, domain):
    skills = domain_skills[domain]
    matched, missing = [], []
    for skill in skills:
        if fuzzy_skill_match(text, skill):
            matched.append(skill)
        else:
            missing.append(skill)
    return matched, missing

def calculate_ats_score(matched_skills, domain):
    total = sum(domain_skills[domain].values())
    matched = sum(domain_skills[domain][s] for s in matched_skills)
    return round((matched / total) * 100, 2) if total > 0 else 0

def generate_report(data):
    return pd.DataFrame(data).to_csv(index=False)

# ----------------- Streamlit App UI -------------------
st.set_page_config(page_title="Smart Resume Analyzer", layout="wide")

st.markdown("""
    <h1 style='text-align: center;'>📄 Smart Resume Analyzer</h1>
    <p style='text-align: center; color: gray;'>AI-powered resume screening with ATS scoring</p>
""", unsafe_allow_html=True)

st.sidebar.header("🧾 Instructions")
st.sidebar.markdown("""
- Upload multiple **PDF or TXT** resumes.
- App will detect **domain**, calculate **ATS score**, and show **skill suggestions**.
- You can **download CSV** for all results.
""")

resume_files = st.file_uploader("📁 Upload Resumes (PDF or TXT)", type=["pdf", "txt"], accept_multiple_files=True)

if resume_files:
    st.success(f"✅ {len(resume_files)} file(s) uploaded. Analyzing now...")
    report = []

    for resume in resume_files:
        st.markdown("---")
        st.subheader(f"📎 {resume.name}")

        # Extract text
        if resume.type == "application/pdf":
            text = extract_text_from_pdf(resume)
        else:
            text = resume.read().decode("utf-8")

        domain, _ = detect_domain(text)
        matched, missing = get_matched_and_missing(text, domain)
        score = calculate_ats_score(matched, domain)

        # Domain and Score
        st.markdown(f"**🔍 Predicted Domain:** `{domain}`")
        st.markdown(f"**📈 ATS Score:** `{score}%`")
        st.progress(score / 100)

        # Matched Skills
        if matched:
            matched_badges = " ".join([f"`✅ {s}`" for s in matched])
            st.markdown(f"**✅ Matched Skills ({len(matched)}):**<br>{matched_badges}", unsafe_allow_html=True)

        # Missing Skills
        if missing:
            missing_badges = " ".join([f"`⚠️ {s}`" for s in missing])
            st.markdown(f"**⚠️ Missing Skills ({len(missing)}):**<br>{missing_badges}", unsafe_allow_html=True)
        else:
            st.success("🎯 All key skills for this domain are present!")

        # Add to report
        report.append({
            "Filename": resume.name,
            "Domain": domain,
            "ATS Score (%)": score,
            "Matched Skills": ", ".join(matched),
            "Missing Skills": ", ".join(missing),
        })

    # Download button
    csv = generate_report(report)
    st.download_button("📥 Download CSV Report", csv, file_name="resume_analysis.csv", mime="text/csv")

