import streamlit as st
import bcrypt
import sqlite3
from db import get_conn
from google_auth_oauthlib.flow import Flow
import os
import requests

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
APP_URL = os.getenv("APP_URL")

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]

def require_login_if_needed():
    if "usage_count" not in st.session_state:
        st.session_state.usage_count = 0

    # 1 free usage for guest
    if st.session_state.usage_count < 1:
        return True

    if "user" not in st.session_state:
        return False

    return True

def register_user(email, password):
    conn = get_conn()
    cur = conn.cursor()
    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        cur.execute(
            "INSERT INTO users (email, password_hash, auth_provider) VALUES (?, ?, ?)",
            (email, pw_hash, "local"),
        )
        conn.commit()
        return True, "Registered successfully! You can now login."
    except sqlite3.IntegrityError:
        return False, "❌ This email is already registered. Please login instead."
    finally:
        conn.close()

def login_user(email, password):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT password_hash FROM users WHERE email=? AND auth_provider='local'",
        (email,),
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        return False
    return bcrypt.checkpw(password.encode(), row[0].encode())

def save_google_user(email):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE email=?", (email,))
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO users (email, password_hash, auth_provider) VALUES (?, ?, ?)",
            (email, None, "google"),
        )
        conn.commit()
    conn.close()

def google_login_button():
    if not CLIENT_ID or not CLIENT_SECRET or not APP_URL:
        st.error("Google OAuth env vars not set (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, APP_URL)")
        return

    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [APP_URL],
            }
        },
        scopes=SCOPES,
        redirect_uri=APP_URL,
    )

    auth_url, _ = flow.authorization_url(prompt="consent")
    st.markdown(f"### 🔐 [Login with Google]({auth_url})")

    
       # Handle OAuth callback
    query_params = dict(st.query_params)
    if "code" in query_params:
        code = query_params["code"][0] if isinstance(query_params["code"], list) else query_params["code"]
        flow.fetch_token(code=code)

        creds = flow.credentials
        headers = {"Authorization": f"Bearer {creds.token}"}
        userinfo = requests.get("https://www.googleapis.com/oauth2/v2/userinfo", headers=headers).json()

        email = userinfo.get("email")
        if email:
            save_google_user(email)
            st.session_state.user = email
            st.success(f"Logged in as {email}")
            st.query_params.clear()  # clear URL params
            st.rerun()


def logout():
    for k in ["user", "usage_count"]:
        if k in st.session_state:
            del st.session_state[k]
    st.success("Logged out successfully!")
    st.rerun()
