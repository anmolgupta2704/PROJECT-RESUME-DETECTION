import os
from PyPDF2 import PdfReader
from jinja2 import Environment, FileSystemLoader
import pdfkit
from dotenv import load_dotenv
from google import genai

# ------------------ CONFIGURATION ------------------

load_dotenv()

# Create Gemini client (new SDK)
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# Load templates
env = Environment(loader=FileSystemLoader("templates"))

# wkhtmltopdf configuration
config = pdfkit.configuration(
    wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
)

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




# ------------------------ RESUME RENDER ------------------------
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


def render_resume_pdf(resume_data, template_choice="ats", preview=False):
    """Render resume HTML or convert to PDF."""
    try:
        template = env.get_template(f"template_{template_choice}.html")
        html_content = template.render(resume_data)

        if preview:
            # For Streamlit preview
            return html_content

        options = {
            "page-size": "A4",
            "encoding": "UTF-8",
            "enable-local-file-access": ""
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

def get_latest_skills(domain):
    """Returns skills for selected domain."""
    return domain_skill_map.get(domain, [])
