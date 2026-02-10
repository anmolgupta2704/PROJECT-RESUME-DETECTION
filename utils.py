import os
from PyPDF2 import PdfReader
from jinja2 import Environment, FileSystemLoader
import pdfkit
from dotenv import load_dotenv
from google import genai

# ------------------ CONFIGURATION ------------------

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

# New Gemini SDK client (works on Render)
client = genai.Client(api_key=GOOGLE_API_KEY)

# Load templates
env = Environment(loader=FileSystemLoader("templates"))

# wkhtmltopdf path (Windows local + Linux Render)
WKHTML_PATH = os.getenv("WKHTMLTOPDF_PATH")

if not WKHTML_PATH:
    if os.name == "nt":  # Windows
        WKHTML_PATH = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    else:  # Linux (Render)
        WKHTML_PATH = "/usr/bin/wkhtmltopdf"

config = pdfkit.configuration(wkhtmltopdf=WKHTML_PATH)

# ---------------------------------------------------


def extract_text_from_pdf(file):
    """Extract readable text from PDF."""
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


def enhance_experience_with_ai(experience_text: str) -> str:
    """Enhance resume experience using Gemini AI."""
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


def render_resume_pdf(resume_data, template_choice="ats", preview=False):
    """Render resume HTML or convert to PDF using wkhtmltopdf."""
    try:
        template = env.get_template(f"template_{template_choice}.html")
        html_content = template.render(**resume_data)

        if preview:
            return html_content

        options = {
            "page-size": "A4",
            "encoding": "UTF-8",
            "enable-local-file-access": "",
            "margin-top": "10mm",
            "margin-bottom": "10mm",
            "margin-left": "10mm",
            "margin-right": "10mm",
        }

        pdf_bytes = pdfkit.from_string(
            html_content,
            False,
            options=options,
            configuration=config
        )
        return pdf_bytes

    except Exception as e:
        return f"Error generating PDF: {str(e)}"


# ------------------------ DOMAIN SKILLS ------------------------

domain_skill_map = {
    "Data Science": ["Python", "Pandas", "NumPy", "Scikit-learn", "Matplotlib", "SQL", "Jupyter"],
    "Web Development": ["HTML", "CSS", "JavaScript", "React", "Node.js", "Bootstrap", "Git"],
    "Machine Learning": ["TensorFlow", "PyTorch", "ML Algorithms", "Scikit-learn", "Python"],
    "DevOps": ["Docker", "Kubernetes", "AWS", "CI/CD", "Linux"],
    "Android Development": ["Java", "Kotlin", "XML", "Firebase", "Android Studio"],
    "Software Engineering": ["OOP", "Data Structures", "Algorithms", "Git", "C++", "Java"],
}

def get_latest_skills(domain: str):
    return domain_skill_map.get(domain, [])
