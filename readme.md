# Resume Shortlisting using BERT

This project leverages the MiniLM-L6-v2 variant of BERT to semantically compare job descriptions with candidate resumes. The system ranks resumes based on their relevance to a given job description, enabling efficient and intelligent resume screening.
 #🚀 Features

✅ Semantic similarity matching using BERT embeddings

✅ Ranks resumes based on job description relevance

✅ Web-based interface built with Streamlit

✅ Easy to use and extensible for different job roles
# Setup Instructions
1. Clone the repository
   ```bash
   git clone https://github.com/anmolgupta2704/PROJECT-RESUME-DETECTION.git
   cd PROJECT-RESUME-DETECTION
2. Install dependencies
   ```bash
   pip install -r requirements.txt
3. Run the Streamlit application
    ```bash
    streamlit run app.py
    
# HOW IT IS WORKS
1.The app uses Sentence Transformers with MiniLM-L6-v2 to generate embeddings.

2.It computes cosine similarity between:

3.The job description input

4.The text content extracted from resumes

5.Resumes are then ranked based on the similarity score.
