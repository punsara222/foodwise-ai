"""
frontend/app.py — FoodWise AI Streamlit frontend.

Run with:
    streamlit run frontend/app.py

--------------------------------------------------------------------------
LOGIN INTEGRATION (for whoever is building the login page):
--------------------------------------------------------------------------
This file exposes `render_app()`, which draws the whole search/results
experience and assumes the user is already authenticated. Your login page
should be the thing Streamlit runs first; once you've verified the user
(and however you're tracking that — e.g. st.session_state["user"]), call:

    from frontend.app import render_app
    render_app()

If this file is run directly (as it is now, via the `if __name__` block
at the bottom), it renders standalone with no login gate, so the rest of
the team can preview/demo it before login is wired in. Once login is
ready, either delete that bottom block and import render_app() from your
login file instead, or add a simple guard here, e.g.:

    if not st.session_state.get("user"):
        st.stop()   # or st.switch_page("login.py")
--------------------------------------------------------------------------
"""
import streamlit as st

from api_client import OrchestratorError, check_health, get_recommendations
from styles import CSS
from ui_components import (
    render_error,
    render_example_chips,
    render_hero,
    render_results,
    render_status_pill,
)

st.set_page_config(page_title="FoodWise AI", page_icon="🥗", layout="centered")


def render_app():
    st.markdown(CSS, unsafe_allow_html=True)

    if "query_input" not in st.session_state:
        st.session_state.query_input = ""
    if "results" not in st.session_state:
        st.session_state.results = None
    if "error" not in st.session_state:
        st.session_state.error = None

    render_hero()
    render_status_pill(check_health())

    clicked_example = render_example_chips()
    if clicked_example:
        st.session_state.query_input = clicked_example
        st.session_state.results = None
        st.session_state.error = None

    with st.form(key="search_form", clear_on_submit=False):
        query = st.text_input(
            "What are you in the mood for?",
            key="query_input",
            placeholder="e.g. high-protein dinner under 500 calories, no dairy",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("🔍 Find recipes", use_container_width=True)

    if submitted:
        if not query or not query.strip():
            st.session_state.error = "Type what you're craving first — a word or two is fine."
            st.session_state.results = None
        else:
            with st.spinner("Asking the agents..."):
                try:
                    st.session_state.results = get_recommendations(query.strip())
                    st.session_state.error = None
                except OrchestratorError as exc:
                    st.session_state.error = str(exc)
                    st.session_state.results = None

    if st.session_state.error:
        render_error(st.session_state.error)

    if st.session_state.results:
        render_results(st.session_state.results)


if __name__ == "__main__":
    render_app()
