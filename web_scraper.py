# web_scraper.py  all skill set
domain_skill_map = {
    "Data Science": ["Python", "Pandas", "NumPy", "Scikit-learn", "Matplotlib", "SQL", "Jupyter"],
    "Web Development": ["HTML", "CSS", "JavaScript", "React", "Node.js", "Bootstrap", "Git"],
    "Machine Learning": ["TensorFlow", "PyTorch", "ML Algorithms", "Scikit-learn", "Python"],
    "DevOps": ["Docker", "Kubernetes", "AWS", "CI/CD", "Linux"],
    "Android Development": ["Java", "Kotlin", "XML", "Firebase", "Android Studio"],
    "Software Engineering": ["OOP", "Data Structures", "Algorithms", "Git", "C++", "Java"]
}

def get_latest_skills(domain):
    return domain_skill_map.get(domain, [])
