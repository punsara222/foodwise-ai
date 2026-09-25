"""
frontend/ui_components.py

Reusable render functions, kept separate from app.py so the page logic
stays readable. Everything here writes directly to the Streamlit page.
"""
import html

import streamlit as st

EXAMPLE_QUERIES = [
    "🍗 High-protein dinner under 500 calories, no dairy",
    "🌱 Vegan breakfast, gluten-free",
    "🌶️ Spicy Thai chicken curry",
]


def render_hero():
    st.markdown(
        """
        <div class="fw-hero">
            <h1>🥗 Food<span class="fw-accent">Wise</span> AI</h1>
            <p>Craving something delicious? Tell us what you like, what you need, and what your goals are - our AI agents work together to find the perfect meal for you.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status_pill(is_healthy: bool):
    dot_class = "fw-dot-ok" if is_healthy else "fw-dot-bad"
    label = "Backend connected" if is_healthy else "Backend unreachable"
    st.markdown(
        f"""
        <div style="text-align:center; margin-bottom: 0.75rem;">
            <span class="fw-status"><span class="fw-dot {dot_class}"></span>{label}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_example_chips():
    """Renders clickable example queries. Returns the clicked example, or None."""
    st.markdown("<div style='text-align:center; margin-bottom:0.4rem;'>", unsafe_allow_html=True)
    cols = st.columns(len(EXAMPLE_QUERIES))
    clicked = None
    for col, example in zip(cols, EXAMPLE_QUERIES):
        with col:
            if st.button(example, key=f"chip_{example}", use_container_width=True):
                clicked = example.split(" ", 1)[1]  # strip the leading emoji
    st.markdown("</div>", unsafe_allow_html=True)
    return clicked


def render_constraints_panel(constraints: dict):
    """Shows what the NLP agent understood from the query — good for
    transparency (Responsible AI) and for demoing the pipeline in the viva."""
    pills = []

    for tag in constraints.get("diet_tags", []):
        pills.append(f'<span class="fw-pill fw-pill-diet">🥦 {html.escape(tag)}</span>')
    for tag in constraints.get("exclude_ingredients", []):
        pills.append(f'<span class="fw-pill fw-pill-exclude">🚫 {html.escape(tag)}</span>')
    if constraints.get("meal_type"):
        pills.append(f'<span class="fw-pill fw-pill-meta">🍽️ {html.escape(constraints["meal_type"])}</span>')
    if constraints.get("max_calories"):
        pills.append(f'<span class="fw-pill fw-pill-meta">🔥 under {constraints["max_calories"]} cal</span>')
    if constraints.get("min_protein_g"):
        pills.append(f'<span class="fw-pill fw-pill-meta">💪 {constraints["min_protein_g"]}g+ protein</span>')

    if not pills:
        return

    st.markdown(
        f"""
        <div class="fw-constraints">
            <span class="fw-label">Understood as:</span>{''.join(pills)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _sentiment_badge(label: str) -> str:
    if not label:
        return ""
    icon = {"positive": "😊", "neutral": "😐", "negative": "😕"}.get(label, "")
    return f'<span class="fw-sentiment fw-sentiment-{label}">{icon} {label.title()}</span>'

def _aspect_tags(aspects: dict) -> str:
    if not aspects:
        return ""
    icon = {"positive": "✅", "negative": "❌", "mixed": "➖"}
    tags = []
    for name, sentiment in aspects.items():
        emoji = icon.get(sentiment, "")
        tags.append(f'<span class="fw-pill fw-pill-meta">{emoji} {html.escape(name)}: {html.escape(sentiment)}</span>')
    return f'<div class="fw-aspects">{"".join(tags)}</div>'

def render_recipe_card(rec: dict):
    title = html.escape(rec.get("title", "Untitled recipe"))
    score_pct = max(0, min(100, round(rec.get("match_score", 0) * 100)))
    macros_bits = []
    if rec.get("calories") is not None:
        macros_bits.append(f'{rec["calories"]} cal')
    if rec.get("protein_g") is not None:
        macros_bits.append(f'{rec["protein_g"]}g protein')
    macros = " · ".join(macros_bits)

    why = html.escape(rec.get("why_recommended", ""))
    review_summary = rec.get("review_summary")
    sentiment_html = _sentiment_badge(rec.get("sentiment_label", ""))
    aspects_html = _aspect_tags(rec.get("aspects", {}))

    review_html = ""
    if review_summary:
        review_html = f'<div class="fw-review">“{html.escape(review_summary)}”</div>'

    st.markdown(
        f"""
        <div class="fw-card">
            <div class="fw-card-top">
                <div>
                    <p class="fw-card-title">{title}</p>
                    <div class="fw-macros">{macros}</div>
                </div>
                <div class="fw-score-wrap">
                    <div class="fw-score-label">Match</div>
                    <div class="fw-score-bar-bg">
                        <div class="fw-score-bar-fill" style="width:{score_pct}%;"></div>
                    </div>
                </div>
            </div>
            <div class="fw-why">💡 {why}</div>
            {review_html}
            {sentiment_html}
            {aspects_html}

        </div>
        """,
        unsafe_allow_html=True,
    )


def render_results(data: dict):
    constraints = data.get("parsed_constraints", {})
    recommendations = data.get("recommendations", [])

    render_constraints_panel(constraints)

    if not recommendations:
        render_empty_state(
            "🍽️", "No recipes matched that exactly",
            "Try loosening a constraint — e.g. a higher calorie limit or fewer excluded ingredients.",
        )
        return

    for rec in recommendations:
        render_recipe_card(rec)

    render_disclaimer(data.get("disclaimer", ""))


def render_empty_state(emoji: str, title: str, subtitle: str = ""):
    st.markdown(
        f"""
        <div class="fw-empty">
            <div class="fw-emoji">{emoji}</div>
            <h3>{html.escape(title)}</h3>
            <p>{html.escape(subtitle)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_error(message: str):
    st.error(f"⚠️ {message}")


def render_disclaimer(text: str):
    if not text:
        return
    st.markdown(f'<div class="fw-disclaimer">ℹ️ {html.escape(text)}</div>', unsafe_allow_html=True)