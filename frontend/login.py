"""
frontend/login.py — FoodWise AI login gate.

Run with:
    streamlit run frontend/login.py
"""
import base64
import os

import jwt
import streamlit as st
from streamlit_oauth import OAuth2Component

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from app import render_app

st.set_page_config(page_title="FoodWise AI — Login", page_icon="🥗", layout="wide")

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
REDIRECT_URI = os.getenv("STREAMLIT_REDIRECT_URI", "http://localhost:8501")

AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
REVOKE_URL = "https://oauth2.googleapis.com/revoke"

BG_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "assets", "login_bg.jpg")


def get_base64_image(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def inject_background_css():
    if not os.path.exists(BG_IMAGE_PATH):
        bg_css = ".stApp { background: #1a1a1a; }"
    else:
        bg_base64 = get_base64_image(BG_IMAGE_PATH)
        bg_css = f"""
        .stApp {{
            background-image: url("data:image/jpg;base64,{bg_base64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        """

    st.markdown(
        f"""
        <style>
        {bg_css}

        /* Hide default Streamlit header/footer for a cleaner full-bleed look */
        header[data-testid="stHeader"] {{
            background: transparent;
        }}

        /* ---------- Glassmorphism login card (outer container ONLY) ---------- */
        div.st-key-login_glass_box {{
            background: rgba(255, 255, 255, 0.12) !important;
            backdrop-filter: blur(18px) saturate(180%) !important;
            -webkit-backdrop-filter: blur(18px) saturate(180%) !important;
            border-radius: 24px !important;
            border: 1px solid rgba(255, 255, 255, 0.25) !important;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.37) !important;
            padding: 48px 40px !important;
            margin-top: 12vh;
        }}

        .login-title {{
            font-size: 2.2rem;
            font-weight: 800;
            color: #ffffff;
            margin-bottom: 0.2rem;
            text-align: center;
            text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }}

        .login-subtitle {{
            font-size: 1rem;
            color: rgba(255, 255, 255, 0.85);
            text-align: center;
            margin-bottom: 2rem;
        }}

        .st-key-login_glass_box .stButton button,
        .st-key-login_glass_box iframe {{
            margin: 0 auto;
            display: block;
        }}

        .st-key-login_glass_box iframe {{
            border-radius: 12px !important;
            overflow: hidden;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
        }}

        /* ---------- Logout bar (shown after login, over the same background) ---------- */
        .logout-bar-wrapper {{
            background: rgba(20, 20, 24, 0.55);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 12px;
            padding: 10px 20px;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            height: 100%;
        }}
        .logout-bar-text {{
            color: #ffffff;
            font-size: 0.9rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_login_screen():
    inject_background_css()

    # Empty left column pushes the glass box to the right side of the screen
    left_spacer, right_box = st.columns([1.3, 1], gap="large")

    with right_box:
        with st.container(key="login_glass_box"):
            st.markdown('<div class="login-title">🥗 Welcome to FoodWise AI</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="login-subtitle">Sign in to get personalized recipe recommendations.</div>',
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
                use_container_width=True,
            )

            if result and "token" in result:
                id_token_str = result["token"].get("id_token")
                if id_token_str:
                    # Decode without verification — Google already verified this
                    # token server-side during the OAuth exchange itself; we're
                    # just reading the claims here, not re-validating signature.
                    claims = jwt.decode(id_token_str, options={"verify_signature": False})
                    st.session_state["user"] = {
                        "email": claims.get("email", "unknown"),
                        "name": claims.get("name", "User"),
                    }
                    st.rerun()


def show_logout_bar():
    inject_background_css()

    user = st.session_state["user"]

    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown(
            f'<div class="logout-bar-wrapper"><span class="logout-bar-text">'
            f'Logged in as <strong>{user["name"]}</strong> ({user["email"]})'
            f'</span></div>',
            unsafe_allow_html=True,
        )
    with col2:
        if st.button("Log out", use_container_width=True):
            del st.session_state["user"]
            st.rerun()


if "user" not in st.session_state:
    show_login_screen()
else:
    show_logout_bar()
    render_app()