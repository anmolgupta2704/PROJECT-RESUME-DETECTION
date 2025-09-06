from PyPDF2 import PdfReader
from jinja2 import Environment, FileSystemLoader
import pdfkit

# Template loader
env = Environment(loader=FileSystemLoader("templates"))

# PDFKit configuration (Windows path to wkhtmltopdf)
config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")

# Extract text from PDF
def extract_text_from_pdf(file):
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

# Fake AI enhancer for experience
def enhance_experience_with_ai(experience_text):
    bullets = [line.strip() for line in experience_text.splitlines() if line.strip()]
    enhanced = [f"• Improved: {b}" for b in bullets]
    return "\n".join(enhanced)

# Render Resume (HTML preview or PDF)
def render_resume_pdf(resume_data, template_choice="ats", preview=False):
    template = env.get_template(f"template_{template_choice}.html")
    html_content = template.render(resume_data)

    if preview:
        return html_content

    options = {
        "page-size": "A4",
        "encoding": "UTF-8",
        "enable-local-file-access": ""
    }
    pdf_bytes = pdfkit.from_string(html_content, False, options=options, configuration=config)
    return pdf_bytes
