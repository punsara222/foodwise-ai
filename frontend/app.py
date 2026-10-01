"""
frontend/app.py — FoodWise AI Streamlit frontend.

Run with:
    streamlit run frontend/login.py      ← the real entrypoint, do this

--------------------------------------------------------------------------
LOGIN INTEGRATION
--------------------------------------------------------------------------
This file exposes `render_app()`, which draws the whole search/results
experience and assumes the user is already authenticated. login.py is the
actual entrypoint: it checks st.session_state["user"] and only then calls
render_app().

IMPORTANT: `streamlit run app.py` starts a brand-new Streamlit process
with its OWN session state — login.py is never imported, so there is no
login check to bypass, but there's also no st.session_state["user"] to
ever be set. The `if __name__ == "__main__"` block below used to call
render_app() unconditionally here, which meant anyone who ran (or was
given a link to) app.py directly got straight into the app with no login
at all. It now refuses to render and tells you to run login.py instead.
--------------------------------------------------------------------------
"""
import streamlit as st

from api_client import OrchestratorError, check_health, get_recommendations
from styles import get_css
from ui_components import (
    render_error,
    render_example_chips,
    render_hero,
    render_recipe_detail,
    render_results,
    render_status_pill,
)

st.set_page_config(page_title="FoodWise AI", page_icon="🥗", layout="centered")


def render_app():
    st.markdown(get_css(), unsafe_allow_html=True)

    if "query_input" not in st.session_state:
        st.session_state.query_input = ""
    if "results" not in st.session_state:
        st.session_state.results = None
    if "error" not in st.session_state:
        st.session_state.error = None
    if "view" not in st.session_state:
        st.session_state.view = "results"   # "results" or "detail"
    if "selected_recipe" not in st.session_state:
        st.session_state.selected_recipe = None

    with st.container(key="fw_page_card"):
        if st.session_state.view == "detail" and st.session_state.selected_recipe:
            _render_detail_view()
        else:
            _render_search_view()


def _render_search_view():
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
        clicked_recipe = render_results(st.session_state.results)
        if clicked_recipe:
            st.session_state.selected_recipe = clicked_recipe
            st.session_state.view = "detail"
            st.rerun()


def _render_detail_view():
    if st.button("← Back to results", key="back_to_results"):
        st.session_state.view = "results"
        st.session_state.selected_recipe = None
        st.rerun()

    render_recipe_detail(st.session_state.selected_recipe)


if __name__ == "__main__":
    # See the module docstring: this file has no login check of its own
    # (that's login.py's job). If this ever executes, app.py was run
    # directly instead of through login.py, so there is deliberately no
    # way in — refuse and point whoever did this at the right file.
    if not st.session_state.get("user"):
        st.error(
            "🔒 This page isn't meant to be opened directly.\n\n"
            "Run `streamlit run login.py` instead — that's the file with "
            "the actual sign-in check."
        )
        st.stop()
    render_app()