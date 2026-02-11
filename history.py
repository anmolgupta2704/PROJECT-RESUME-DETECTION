from db import get_conn

def save_resume_history(user_email, domain, score):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO resume_history (user_email, domain, score) VALUES (?, ?, ?)",
        (user_email, domain, score),
    )
    conn.commit()
    conn.close()

def get_resume_history(user_email):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT domain, score, created_at FROM resume_history WHERE user_email=? ORDER BY created_at DESC",
        (user_email,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows
