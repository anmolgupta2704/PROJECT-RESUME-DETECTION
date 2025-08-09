import streamlit as st
from model import encode_text, compute_similarity
from utils import extract_text_from_pdf

st.set_page_config(page_title="Resume Shortlisting with BERT")
st.title("📄 Resume Shortlisting using BERT (High Accuracy)")

jd_file = st.file_uploader("Upload Job Description (PDF or TXT)", type=["pdf", "txt"])
resume_files = st.file_uploader("Upload Multiple Resumes", type=["pdf", "txt"], accept_multiple_files=True)

if jd_file and resume_files:
    # Read JD
    if jd_file.type == "application/pdf":
        jd_text = extract_text_from_pdf(jd_file)
    else:
        jd_text = jd_file.read().decode("utf-8")

    jd_embedding = encode_text(jd_text)
    results = []

    for resume in resume_files:
        if resume.type == "application/pdf":
            resume_text = extract_text_from_pdf(resume)
        else:
            resume_text = resume.read().decode("utf-8")

        similarity = compute_similarity(jd_text, resume_text)
        results.append((resume.name, similarity))

    sorted_results = sorted(results, key=lambda x: x[1], reverse=True)

    st.subheader("📊 Resume Ranking (Using BERT Cosine Similarity)")
    for i, (name, score) in enumerate(sorted_results, 1):
        st.write(f"{i}. *{name}* — Similarity Score: {round(score * 100, 2)}%")