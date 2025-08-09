Project: Resume Shortlisting using BERT (High Accuracy)

✅ Folder Structure

resume-shortlisting-bert/
├── app.py                  ← Main Streamlit app
├── model.py                ← BERT logic (modular)
├── utils.py                ← PDF text extraction
├── requirements.txt        ← Python dependencies
└── README.md               ← Documentation


---

✅ app.py

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


---

✅ model.py

from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

def encode_text(text):
    return model.encode(text, convert_to_tensor=True)

def compute_similarity(text1, text2):
    emb1 = encode_text(text1)
    emb2 = encode_text(text2)
    return util.cos_sim(emb1, emb2).item()


---

✅ utils.py

import pdfplumber

def extract_text_from_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text


---

✅ requirements.txt

streamlit
sentence-transformers
pdfplumber


---

✅ README.md (short version)

# Resume Shortlisting using BERT

This project uses BERT (MiniLM-L6-v2) to semantically compare job descriptions and resumes, ranking them based on relevance.

## 🔧 Setup
```bash
pip install -r requirements.txt
streamlit run app.py 