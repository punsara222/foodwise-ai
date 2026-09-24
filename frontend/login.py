"""
frontend/login.py — FoodWise AI login gate.
"""
import os

import streamlit as st
from streamlit_oauth import OAuth2Component

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from app import render_app

st.set_page_config(page_title="FoodWise AI — Login", page_icon="🥗", layout="centered")

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
REDIRECT_URI = os.getenv("STREAMLIT_REDIRECT_URI", "http://localhost:8501")

AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
REVOKE_URL = "https://oauth2.googleapis.com/revoke"


def show_login_screen():
    st.markdown("<h1 style='text-align:center;'>🥗 FoodWise AI</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center;'>Sign in to get personalized recipe recommendations.</p>",
        unsafe_allow_html=True,
    )

    if not CLIENT_ID or not CLIENT_SECRET:
        st.error(
            "Google sign-in isn't configured yet — GOOGLE_CLIENT_ID and "
            "GOOGLE_CLIENT_SECRET are missing from frontend/.env."
        )
        return

    oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZE_URL, TOKEN_URL, TOKEN_URL, REVOKE_URL)

    result = oauth2.authorize_button(
        name="Sign in with Google",
        icon="https://www.google.com.tw/favicon.ico",
        redirect_uri=REDIRECT_URI,
        scope="openid email profile",
        key="google_login",
    )

    if result and "token" in result:
        claims = result["token"].get("id_token_claims", {})
        st.session_state["user"] = {
            "email": claims.get("email", "unknown"),
            "name": claims.get("name", "User"),
        }
        st.rerun()


def show_logout_bar():
    user = st.session_state["user"]
    col1, col2 = st.columns([4, 1])
    with col1:
        st.caption(f"Logged in as {user['name']} ({user['email']})")
    with col2:
        if st.button("Log out"):
            del st.session_state["user"]
            st.rerun()


if "user" not in st.session_state:
    show_login_screen()
else:
    show_logout_bar()
    render_app()