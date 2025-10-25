import os
from PyPDF2 import PdfReader
from jinja2 import Environment, FileSystemLoader
import pdfkit
import google.generativeai as genai
from dotenv import load_dotenv

# ------------------ CONFIGURATION ------------------

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Template loader
env = Environment(loader=FileSystemLoader("templates"))

# PDFKit configuration (Update this path if wkhtmltopdf is installed elsewhere)
config = pdfkit.configuration(
    wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
)

# ------------------ FUNCTIONS ------------------

# ✅ Extract text from PDF
def extract_text_from_pdf(file):
    """Extracts readable text from a PDF file."""
    try:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
        return text.strip()
    except Exception as e:
        return f"Error reading PDF: {str(e)}"


# ✅ Enhance resume experience using Gemini AI
def enhance_experience_with_ai(experience_text):
    """Uses Google Gemini AI to rewrite or improve experience points."""
    try:
        # Use Gemini 1.5 Pro (stable model)
        model = genai.GenerativeModel("gemini-1.5-flash-latest")

        prompt = f"""
        Improve the following resume experience points to look professional, ATS-friendly,
        and impactful. Use bullet points and strong action verbs. Keep it concise.

        Experience:
        {experience_text}
        """

        response = model.generate_content(prompt)
        return response.text.strip() if response and response.text else experience_text

    except Exception as e:
        return f"⚠️ AI Suggestion Error: {str(e)}"


# ✅ Render resume (HTML or PDF)
def render_resume_pdf(resume_data, template_choice="ats", preview=False):
    """Renders the resume into HTML or PDF using Jinja2 and pdfkit."""
    try:
        template = env.get_template(f"template_{template_choice}.html")
        html_content = template.render(resume_data)

        if preview:
            return html_content  # For Streamlit live preview

        options = {
            "page-size": "A4",
            "encoding": "UTF-8",
            "enable-local-file-access": ""
        }

        pdf_bytes = pdfkit.from_string(
            html_content, False, options=options, configuration=config
        )
        return pdf_bytes

    except Exception as e:
        return f"Error generating PDF: {str(e)}"


# ✅ Domain → Skills mapping
domain_skill_map = {
    "Data Science": ["Python", "Pandas", "NumPy", "Scikit-learn", "Matplotlib", "SQL", "Jupyter"],
    "Web Development": ["HTML", "CSS", "JavaScript", "React", "Node.js", "Bootstrap", "Git"],
    "Machine Learning": ["TensorFlow", "PyTorch", "ML Algorithms", "Scikit-learn", "Python"],
    "DevOps": ["Docker", "Kubernetes", "AWS", "CI/CD", "Linux"],
    "Android Development": ["Java", "Kotlin", "XML", "Firebase", "Android Studio"],
    "Software Engineering": ["OOP", "Data Structures", "Algorithms", "Git", "C++", "Java"]
}

def get_latest_skills(domain):
    """Returns the list of trending skills for a selected domain."""
    return domain_skill_map.get(domain, [])
