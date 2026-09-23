# frontend/ — Streamlit UI

The screen users interact with. Sends the user's query to the orchestrator
and renders the recommendations as recipe cards.

## What's in here

```
frontend/
├── app.py              Main entrypoint — run with `streamlit run app.py`
├── api_client.py        Talks to the orchestrator's HTTP API
├── ui_components.py     Reusable render functions (cards, hero, pills...)
├── styles.py             Custom CSS (cream/brown/tomato/sage theme)
├── requirements.txt
└── .env.example
```

## Setup

```bash
cd frontend
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

`.env` points at the orchestrator (defaults to `http://localhost:8000`
with the dev API key) — only change it if Patali's orchestrator is running
somewhere else or the API key changes.

## Running it

Make sure the backend is running first — the orchestrator plus all three
agents (`query_agent`, `retrieval_agent`, `review_agent`). See the main
project README or `orchestrator/README.md` for how to start those.

Then:
```bash
streamlit run app.py
```
Opens at **http://localhost:8501**. The green/red status pill under the
title tells you at a glance whether it can reach the orchestrator.

## What it does

- A hero header, a search box, and four clickable example queries.
- On submit, calls `POST /api/v1/query` on the orchestrator with the query
  text.
- Shows a **"Understood as:"** panel with pills for the diet tags,
  excluded ingredients, calorie/protein limits, and meal type the query
  agent extracted — this doubles as a nice transparency/demo moment for
  the viva (Responsible AI: explainability).
- Renders each recommendation as a card: title, calories/protein, a match
  score bar, a plain-language "why recommended" reason, a quoted review
  summary, and a sentiment badge.
- Shows the orchestrator's Responsible AI disclaimer at the bottom.
- Friendly error states if the backend, or any individual agent, is
  unreachable — never a raw stack trace.

## Login integration

This file is built to run standalone for now so the team can preview it
without waiting on login. Whoever owns the login page should read the
comment block at the top of `app.py` — short version: `app.py` exposes a
`render_app()` function that draws everything *after* auth is confirmed.
Import that function from the login page and call it once the user is
authenticated, instead of running `app.py` directly.

## Testing it without a browser

Streamlit ships a headless test API that's useful for CI or quick checks:
```python
from streamlit.testing.v1 import AppTest

at = AppTest.from_file("app.py")
at.run()
assert not at.exception

at.text_input(key="query_input").set_value("vegan dinner")
at.button[-1].click()
at.run()
assert not at.exception
```
(Needs the backend running to get real results back instead of the error
state.)
