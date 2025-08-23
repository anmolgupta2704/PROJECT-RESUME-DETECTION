# 📄 Smart Resume Analyzer (Domain-Based ATS)

This is a Streamlit-based **Smart Resume Analyzer** tool built for academic or portfolio use. It allows users to:

✅ Select their career domain  
✅ Upload their resume (PDF or TXT)  
✅ Automatically match their skills with the **required skills** for that domain  
✅ See an **ATS (Applicant Tracking System) score**  
✅ Download a CSV report with matched and missing skills

---

## 🚀 Features

- Manual **domain selection** (Data Science, Web Dev, ML, etc.)
- Extracts text from PDF or TXT resume
- Matches your skills against a **predefined skill set**
- Displays:
  - ✅ Matched skills
  - ⚠️ Missing skills
  - 📊 ATS Score
- Downloadable CSV report

---

## 🧠 How Skill Matching Works

- A set of **important skills** for each domain is defined manually
- Your resume is scanned and matched against those using fuzzy logic
- Based on matches, an ATS score is calculated
- Suggestions for improvement are shown

---

## 📁 How to Run

1. **Clone or download** this repository
2. Create a virtual environment (optional but recommended)

   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # For Windows
👨‍💻 Author

Made with ❤️ for academic/project use.


---
## Install dependencies
```bash
pip install -r requirements.txt

```
## Run the app
```bash
streamlit run app.py
```
```bash
Open browser at http://localhost:8501
```
📝 File Structure
Now just make sure your folder includes:

```bash
📁 PROJECT RESUME DETECTION
├── app.py
├── utils.py
├── requirements.txt
└── README.md
