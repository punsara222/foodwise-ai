"""
frontend/styles.py

Custom look for FoodWise AI — warm, food-themed palette (matches the
cream/brown/tomato/sage tones from the team's mid-eval deck), injected as
raw CSS since Streamlit's defaults are pretty generic on their own.

CSS is now built by get_css() instead of being a flat string, because the
background photo has to be embedded as a base64 data URI — Streamlit has
no way to reference a local image file from inside a CSS url().
"""
import base64
from pathlib import Path

BASE_DIR = Path(__file__).parent
DEFAULT_BG_IMAGE = BASE_DIR / "assets" / "food.jpg"


def _image_to_base64(image_path: Path) -> str | None:
    """Reads an image file and returns it base64-encoded, or None if the
    file isn't there — so a missing image degrades gracefully to the
    plain gradient background instead of crashing the app."""
    try:
        return base64.b64encode(image_path.read_bytes()).decode()
    except FileNotFoundError:
        return None


def get_css(bg_image_path: Path = DEFAULT_BG_IMAGE) -> str:
    bg_base64 = _image_to_base64(bg_image_path)

    if bg_base64:
        # Dark overlay (a semi-transparent black gradient) stacked on top
        # of the photo, so the photo is visibly "a bit darkened" per the
        # sketch, and the light card in front of it stays easy to read.
        #
        # The two background-* properties below are comma-separated lists,
        # one value per layer, matching the order in `background:` above
        # (gradient layer first, photo layer second):
        #   - background-size:  "cover, 94%"   → the gradient still fully
        #     covers the page; the photo is sized to 94% instead of cover's
        #     100%+, so slightly less of it gets cropped off ("zoomed out"
        #     a little) and more of the photo is visible.
        #   - background-repeat: must be "no-repeat, no-repeat" — once a
        #     layer's size drops below full coverage, the default repeat
        #     behaviour would tile it into multiple copies.
        # Adjust the 94% to zoom in (raise it) or out further (lower it).
        app_bg_rules = f"""
            background: linear-gradient(rgba(20, 12, 4, 0.55), rgba(20, 12, 4, 0.55)),
                        url("data:image/jpeg;base64,{bg_base64}");
            background-color: #1f150d;
            background-repeat: no-repeat, no-repeat;
            background-size: cover, 100%;
            background-position: center, center;
            background-attachment: fixed, fixed;
        """
    else:
        app_bg_rules = """
            background: linear-gradient(180deg, #FFF8EE 0%, #FBEEDB 100%);
        """

    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@500;600;700&family=Poppins:wght@400;500;600&display=swap');

    :root {{
        --cream: #FFF8EE;
        --cream-deep: #FBEEDB;
        --brown: #6B3F1D;
        --brown-soft: #8B5E34;
        --tomato: #E4572E;
        --tomato-soft: #F2825E;
        --sage: #6E8B5A;
        --sage-soft: #A9C199;
    }}

    /* App background — the darkened photo behind everything */
    [data-testid="stAppViewContainer"] {{
        {app_bg_rules}
    }}
    [data-testid="stHeader"] {{ background: transparent; }}

    /* Streamlit's layout="centered" caps its own container at roughly
       736px — wider than that, our card's max-width above would get
       clipped by this outer cap instead of taking effect. Remove it so
       our card's own max-width is what actually governs the width. */
    [data-testid="stAppViewContainer"] .block-container,
    [data-testid="stMainBlockContainer"] {{
        max-width: none !important;
    }}

    /* The floating light card that holds all app content, per the sketch.
       This targets Streamlit's auto-generated class for a keyed
       st.container(key="fw_page_card") — NOT a raw HTML div. A manually
       opened/unclosed <div> in one st.markdown() call can't wrap elements
       from later, separate st.* calls: each st.markdown() renders its
       HTML into its own isolated React-managed node, so the browser
       auto-closes any unclosed tag right there instead of letting it
       span later elements. st.container(key=...) is a real Streamlit
       container, so everything placed inside it is an actual DOM child. */
    .st-key-fw_page_card {{
        max-width: 1100px;
        margin: 3rem auto;
        background: linear-gradient(180deg, var(--cream) 0%, var(--cream-deep) 100%);
        border-radius: 28px;
        padding: 3.5rem 3.75rem 4rem 3.75rem;
        box-shadow: 0 25px 60px rgba(0, 0, 0, 0.35);
    }}
    @media (max-width: 640px) {{
        .st-key-fw_page_card {{
            margin: 1.25rem;
            padding: 2rem 1.5rem 2.25rem 1.5rem;
            border-radius: 20px;
        }}
    }}

    /* Base typography */
    html, body, [class*="css"] {{
        font-family: 'Poppins', sans-serif;
        color: var(--brown);
    }}
    h1, h2, h3 {{ font-family: 'Quicksand', sans-serif; }}

    /* Hero */
    .fw-hero {{
        text-align: center;
        padding: 0.5rem 1rem 1.25rem 1rem;
    }}
    .fw-hero h1 {{
        font-size: 2.6rem;
        font-weight: 700;
        color: var(--brown);
        margin-bottom: 0.15rem;
    }}
    .fw-hero .fw-accent {{ color: var(--tomato); }}
    .fw-hero p {{
        font-size: 1.05rem;
        color: var(--brown-soft);
        margin-top: 0;
    }}

    /* Status pill */
    .fw-status {{
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.8rem;
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        background: #ffffffaa;
        border: 1px solid #eadfce;
        color: var(--brown-soft);
    }}
    .fw-dot {{ width: 8px; height: 8px; border-radius: 50%; display: inline-block; }}
    .fw-dot-ok {{ background: var(--sage); }}
    .fw-dot-bad {{ background: var(--tomato); }}

    /* Example chips */
    /* Streamlit's default button CSS clips long labels with overflow:hidden +
       ellipsis, and adds a title="" attribute (the hover tooltip) when it
       detects the clip. We override every layer using data-testid selectors
       (stable across versions) plus a universal "*" selector. */
    .stButton > button,
    [data-testid="stButton"] button,
    [data-testid^="stBaseButton"] {{
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
    }}
    .stButton > button:hover,
    [data-testid="stButton"] button:hover,
    [data-testid^="stBaseButton"]:hover {{
        border-color: var(--tomato) !important;
        color: var(--tomato) !important;
        transform: translateY(-1px);
    }}
    .stButton > button *,
    [data-testid="stButton"] button *,
    [data-testid^="stBaseButton"] *,
    [data-testid="stMarkdownContainer"] p {{
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: unset !important;
    }}
    [data-testid="stHorizontalBlock"] {{
        align-items: stretch !important;
        gap: 1rem !important;
    }}

    /* Primary search button */
    div[data-testid="stFormSubmitButton"] > button {{
        background: var(--tomato) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.4rem !important;
    }}
    div[data-testid="stFormSubmitButton"] > button:hover {{
        background: var(--tomato-soft) !important;
        transform: translateY(-1px);
    }}

    /* Spinner ("Asking the agents...") — inherits the theme's text color
       by default, which can be near-white; force it explicitly. */
    [data-testid="stSpinner"],
    [data-testid="stSpinner"] p,
    [data-testid="stSpinner"] div,
    [data-testid="stSpinner"] span {{
        color: var(--brown) !important;
    }}

    /* Search input — same near-invisible-text risk as the spinner, since
       we force the background to white but must also force the text
       color, or a dark-mode visitor gets white-on-white. */
    .stTextInput input {{
        border-radius: 12px !important;
        border: 1.5px solid #eadfce !important;
        padding: 0.7rem 1rem !important;
        font-size: 1rem !important;
        background: white !important;
        color: var(--brown) !important;
        -webkit-text-fill-color: var(--brown) !important;
    }}
    .stTextInput input::placeholder {{
        color: var(--brown-soft) !important;
        opacity: 0.65 !important;
    }}
    .stTextInput input:focus {{
        border-color: var(--tomato) !important;
        box-shadow: 0 0 0 3px rgba(228, 87, 46, 0.15) !important;
    }}

    /* Constraints panel */
    .fw-constraints {{
        background: #ffffffb0;
        border: 1px dashed #e0d2ba;
        border-radius: 14px;
        padding: 0.9rem 1.1rem;
        margin: 0.75rem 0 1.25rem 0;
        font-size: 0.88rem;
    }}
    .fw-constraints .fw-label {{
        font-weight: 600;
        color: var(--brown-soft);
        margin-right: 0.4rem;
    }}
    .fw-pill {{
        display: inline-block;
        padding: 0.2rem 0.65rem;
        border-radius: 999px;
        font-size: 0.78rem;
        margin: 0.15rem 0.25rem 0.15rem 0;
        font-weight: 500;
    }}
    .fw-pill-diet {{ background: #E9F1E2; color: var(--sage); }}
    .fw-pill-exclude {{ background: #FBE7E1; color: var(--tomato); }}
    .fw-pill-meta {{ background: #F1E6D8; color: var(--brown-soft); }}

    /* Recipe card */
    .fw-card {{
        background: white;
        border-radius: 18px;
        padding: 1.25rem 1.4rem;
        margin-bottom: 1.1rem;
        box-shadow: 0 4px 18px rgba(107, 63, 29, 0.08);
        border: 1px solid #f1e6d6;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}
    .fw-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 10px 26px rgba(107, 63, 29, 0.14);
    }}
    .fw-card-top {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 0.75rem;
    }}
    .fw-card-title {{
        font-family: 'Quicksand', sans-serif;
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--brown);
        margin: 0;
    }}
    .fw-macros {{
        font-size: 0.85rem;
        color: var(--brown-soft);
        margin-top: 0.2rem;
    }}
    .fw-score-wrap {{
        min-width: 92px;
        text-align: right;
    }}
    .fw-score-label {{
        font-size: 0.7rem;
        color: var(--brown-soft);
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }}
    .fw-score-bar-bg {{
        width: 90px;
        height: 6px;
        border-radius: 4px;
        background: #f1e6d6;
        margin-top: 0.25rem;
        overflow: hidden;
    }}
    .fw-score-bar-fill {{
        height: 100%;
        border-radius: 4px;
        background: linear-gradient(90deg, var(--sage-soft), var(--sage));
    }}
    .fw-why {{
        font-size: 0.88rem;
        color: var(--brown);
        background: #FBF3E6;
        border-radius: 10px;
        padding: 0.55rem 0.8rem;
        margin: 0.75rem 0 0.6rem 0;
    }}
    .fw-review {{
        font-size: 0.85rem;
        color: var(--brown-soft);
        font-style: italic;
        border-left: 3px solid #eadfce;
        padding-left: 0.7rem;
        margin-top: 0.5rem;
    }}
    .fw-sentiment {{
        display: inline-block;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.15rem 0.6rem;
        border-radius: 999px;
        margin-top: 0.5rem;
    }}
    .fw-sentiment-positive {{ background: #E9F1E2; color: var(--sage); }}
    .fw-sentiment-neutral {{ background: #F1E6D8; color: var(--brown-soft); }}
    .fw-sentiment-negative {{ background: #FBE7E1; color: var(--tomato); }}

    /* Disclaimer footer */
    .fw-disclaimer {{
        text-align: center;
        font-size: 0.78rem;
        color: var(--brown-soft);
        background: #ffffffaa;
        border-radius: 12px;
        padding: 0.7rem 1rem;
        margin-top: 1.5rem;
        border: 1px solid #eadfce;
    }}

    /* Empty / error states */
    .fw-empty {{
        text-align: center;
        padding: 2.5rem 1rem;
        color: var(--brown-soft);
    }}
    .fw-empty .fw-emoji {{ font-size: 2.4rem; }}

    footer, #MainMenu {{ visibility: hidden; }}
    </style>
    """