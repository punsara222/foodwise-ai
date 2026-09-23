"""
frontend/styles.py

Custom look for FoodWise AI — warm, food-themed palette (matches the
cream/brown/tomato/sage tones from the team's mid-eval deck), injected as
raw CSS since Streamlit's defaults are pretty generic on their own.
"""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@500;600;700&family=Poppins:wght@400;500;600&display=swap');

:root {
    --cream: #FFF8EE;
    --cream-deep: #FBEEDB;
    --brown: #6B3F1D;
    --brown-soft: #8B5E34;
    --tomato: #E4572E;
    --tomato-soft: #F2825E;
    --sage: #6E8B5A;
    --sage-soft: #A9C199;
}

/* App background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, var(--cream) 0%, var(--cream-deep) 100%);
}
[data-testid="stHeader"] { background: transparent; }

/* Base typography */
html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
    color: var(--brown);
}
h1, h2, h3 { font-family: 'Quicksand', sans-serif; }

/* Hero */
.fw-hero {
    text-align: center;
    padding: 1.75rem 1rem 0.5rem 1rem;
}
.fw-hero h1 {
    font-size: 2.6rem;
    font-weight: 700;
    color: var(--brown);
    margin-bottom: 0.15rem;
}
.fw-hero .fw-accent { color: var(--tomato); }
.fw-hero p {
    font-size: 1.05rem;
    color: var(--brown-soft);
    margin-top: 0;
}

/* Status pill */
.fw-status {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.8rem;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    background: #ffffffaa;
    border: 1px solid #eadfce;
    color: var(--brown-soft);
}
.fw-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.fw-dot-ok { background: var(--sage); }
.fw-dot-bad { background: var(--tomato); }

/* Example chips */
/* Streamlit's default button CSS clips long labels with overflow:hidden +
   ellipsis, and adds a title="" attribute (that's the hover tooltip you
   were seeing) when it detects the clip. We override every layer —
   button, and EVERY descendant regardless of depth or Streamlit version —
   using data-testid selectors (stable across versions) plus a universal
   "*" selector, so nothing sneaks past. */
.stButton > button,
[data-testid="stButton"] button,
[data-testid^="stBaseButton"] {
    border-radius: 999px !important;
    border: 1px solid #eadfce !important;
    background: #ffffffcc !important;
    color: var(--brown) !important;
    font-size: 0.85rem !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.15s ease-in-out;

    height: auto !important;
    min-height: 2.6rem;
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: unset !important;
    line-height: 1.3 !important;
    word-break: break-word !important;
}
.stButton > button:hover,
[data-testid="stButton"] button:hover,
[data-testid^="stBaseButton"]:hover {
    border-color: var(--tomato) !important;
    color: var(--tomato) !important;
    transform: translateY(-1px);
}
/* Catch every nested wrapper (div/p/span/etc.) inside the button, at any
   depth, so the label text can never be clipped independently of the
   button's own override above. */
.stButton > button *,
[data-testid="stButton"] button *,
[data-testid^="stBaseButton"] *,
[data-testid="stMarkdownContainer"] p {
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: unset !important;
}
/* Keep all four chips in a row the same height even after wrapping. */
[data-testid="stHorizontalBlock"] {
    align-items: stretch !important;
}

/* Primary search button */
div[data-testid="stFormSubmitButton"] > button {
    background: var(--tomato) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.4rem !important;
}
div[data-testid="stFormSubmitButton"] > button:hover {
    background: var(--tomato-soft) !important;
    transform: translateY(-1px);
}

/* Search input */
.stTextInput input {
    border-radius: 12px !important;
    border: 1.5px solid #eadfce !important;
    padding: 0.7rem 1rem !important;
    font-size: 1rem !important;
    background: white !important;
}
.stTextInput input:focus {
    border-color: var(--tomato) !important;
    box-shadow: 0 0 0 3px rgba(228, 87, 46, 0.15) !important;
}

/* Constraints panel */
.fw-constraints {
    background: #ffffffb0;
    border: 1px dashed #e0d2ba;
    border-radius: 14px;
    padding: 0.9rem 1.1rem;
    margin: 0.75rem 0 1.25rem 0;
    font-size: 0.88rem;
}
.fw-constraints .fw-label {
    font-weight: 600;
    color: var(--brown-soft);
    margin-right: 0.4rem;
}
.fw-pill {
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 999px;
    font-size: 0.78rem;
    margin: 0.15rem 0.25rem 0.15rem 0;
    font-weight: 500;
}
.fw-pill-diet { background: #E9F1E2; color: var(--sage); }
.fw-pill-exclude { background: #FBE7E1; color: var(--tomato); }
.fw-pill-meta { background: #F1E6D8; color: var(--brown-soft); }

/* Recipe card */
.fw-card {
    background: white;
    border-radius: 18px;
    padding: 1.25rem 1.4rem;
    margin-bottom: 1.1rem;
    box-shadow: 0 4px 18px rgba(107, 63, 29, 0.08);
    border: 1px solid #f1e6d6;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.fw-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 26px rgba(107, 63, 29, 0.14);
}
.fw-card-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 0.75rem;
}
.fw-card-title {
    font-family: 'Quicksand', sans-serif;
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--brown);
    margin: 0;
}
.fw-macros {
    font-size: 0.85rem;
    color: var(--brown-soft);
    margin-top: 0.2rem;
}
.fw-score-wrap {
    min-width: 92px;
    text-align: right;
}
.fw-score-label {
    font-size: 0.7rem;
    color: var(--brown-soft);
    text-transform: uppercase;
    letter-spacing: 0.03em;
}
.fw-score-bar-bg {
    width: 90px;
    height: 6px;
    border-radius: 4px;
    background: #f1e6d6;
    margin-top: 0.25rem;
    overflow: hidden;
}
.fw-score-bar-fill {
    height: 100%;
    border-radius: 4px;
    background: linear-gradient(90deg, var(--sage-soft), var(--sage));
}
.fw-why {
    font-size: 0.88rem;
    color: var(--brown);
    background: #FBF3E6;
    border-radius: 10px;
    padding: 0.55rem 0.8rem;
    margin: 0.75rem 0 0.6rem 0;
}
.fw-review {
    font-size: 0.85rem;
    color: var(--brown-soft);
    font-style: italic;
    border-left: 3px solid #eadfce;
    padding-left: 0.7rem;
    margin-top: 0.5rem;
}
.fw-sentiment {
    display: inline-block;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.15rem 0.6rem;
    border-radius: 999px;
    margin-top: 0.5rem;
}
.fw-sentiment-positive { background: #E9F1E2; color: var(--sage); }
.fw-sentiment-neutral { background: #F1E6D8; color: var(--brown-soft); }
.fw-sentiment-negative { background: #FBE7E1; color: var(--tomato); }

/* Disclaimer footer */
.fw-disclaimer {
    text-align: center;
    font-size: 0.78rem;
    color: var(--brown-soft);
    background: #ffffffaa;
    border-radius: 12px;
    padding: 0.7rem 1rem;
    margin-top: 1.5rem;
    border: 1px solid #eadfce;
}

/* Empty / error states */
.fw-empty {
    text-align: center;
    padding: 2.5rem 1rem;
    color: var(--brown-soft);
}
.fw-empty .fw-emoji { font-size: 2.4rem; }

footer, #MainMenu { visibility: hidden; }
</style>
"""