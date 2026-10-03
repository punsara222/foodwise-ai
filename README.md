# 🥗 FoodWise AI

**A Multi-Agent Recipe & Nutrition Assistant**

FoodWise AI understands natural-language food requests — like *"high-protein dinner under 500 calories, no dairy"* — and returns personalized, explainable recipe recommendations. It parses the request into structured constraints, retrieves matching recipes from a nutrition dataset, analyzes real user reviews, and returns a ranked list of recipes with a plain-language reason for each one.

Built for **IT3041 – Information Retrieval and Web Analytics**, as a group project demonstrating agentic AI, NLP, information retrieval, security, and Responsible AI practices.

---

## Overview

Existing recipe platforms rely on keyword search, not genuine constraint understanding — a query like *"under 500 calories, no dairy"* gets treated as a text match rather than parsed into real filters. FoodWise AI solves this with a pipeline of cooperating agents, each responsible for one stage of reasoning:

1. **Understand** the query → structured constraints
2. **Retrieve** matching recipes → ranked by relevance
3. **Analyze** what real reviewers said → sentiment & summary
4. **Recommend** → merged, ranked, explainable final answer

## Architecture

```
┌──────────┐      ┌──────────────┐      ┌─────────────────┐      ┌───────────────┐
│          │─────▶│ Orchestrator │─────▶│  Query Agent     │      │               │
│ Frontend │      │ (routing +   │      │  (NLP + LLM)     │      │  Recommend-   │
│ Streamlit│◀─────│  security)   │◀─────│                  │      │  ation Agent  │
│          │      │              │─────▶│  Retrieval Agent │─────▶│  (merges      │
└──────────┘      │              │◀─────│  (TF-IDF)        │      │   results)    │
                   │              │─────▶│  Review Agent    │◀─────┘               │
                   │              │◀─────│  (VADER)         │
                   └──────────────┘      └──────────────────┘
```

A user query flows: **Orchestrator → Query Agent → Retrieval Agent → Review Agent → Recommendation Agent → back to the user.** Each arrow is an independent HTTP call with its own error handling, so one agent being unavailable doesn't take down the rest of the pipeline.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend framework | FastAPI (Python) |
| Frontend | Streamlit |
| NLP / Query parsing | Rule-based entity extraction + keyword/intent detection, supplemented by an LLM |
| LLM (structured extraction) | OpenAI API (`gpt-4o-mini`) — fills gaps rule-based parsing misses, constrained to JSON output |
| Information Retrieval | TF-IDF vectorization + cosine similarity, metadata filtering (scikit-learn) |
| Sentiment analysis | VADER (rule-based lexicon) |
| Summarization | Extractive summarization (frequency-scored sentence selection) |
| Authentication | Google OAuth 2.0 (frontend login) + API-key auth (backend) |
| Dataset | Food.com recipes & reviews (Kaggle) |
| Inter-agent communication | HTTP / REST (FastAPI), JSON validated against shared Pydantic schemas |
| Version control | Git & GitHub (feature-branch workflow with pull requests) |

## Project Structure

```
foodwise-ai/
├── orchestrator/        # Routing, security, Recommendation Agent — owned by P A Tennakoon
│   ├── main.py
│   ├── schemas.py        # THE CONTRACT — shared data shapes every agent must match
│   ├── security.py        # Auth, input sanitization, rate limiting
│   ├── recommendation_agent.py
│   ├── clients/            # HTTP clients to the other three agents
│   ├── routers/
│   ├── mocks/              # Mock agents for independent testing
│   └── tests/
├── query_agent/          # NLP + LLM constraint extraction — owned by S R M P T Rathnayake
├── retrieval_agent/      # TF-IDF + cosine similarity search — owned by K A G T N Waidyarathne
├── review_agent/         # Sentiment, aspects, summarization — owned by M D A K Mahagamage
├── frontend/             # Streamlit UI + Google OAuth login — owned by P A Tennakoon
│   ├── login.py            # Entry point — handles auth, then renders app.py
│   ├── app.py
│   ├── ui_components.py
│   └── styles.py
├── data/                 # Cleaned dataset (recipes_clean.parquet, reviews CSV)
├── docs/                 # Architecture diagrams, viva prep, report assets
└── notebooks/            # Exploratory / data-cleaning notebooks
```

## Setup & Installation

Each agent and the frontend run as **separate services** with their own dependencies. Use a separate virtual environment per folder, or one shared environment for the whole repo — either works.

### 1. Clone and prepare data

```bash
git clone <repo-url>
cd foodwise-ai
```

Make sure `data/recipes_clean.parquet` and `data/foodwise_final_dataset.csv` exist. If not, run the preprocessing script first:

```bash
cd retrieval_agent
python3 preprocess.py
cd ..
```

### 2. Install dependencies for each service

```bash
pip install -r orchestrator/requirements.txt
pip install -r query_agent/requirements.txt
pip install -r retrieval_agent/requirements.txt
pip install -r review_agent/requirements.txt
pip install -r frontend/requirements.txt
```

### 3. Configure environment variables

Each service that needs one has a `.env.example` — copy it to `.env` in the same folder and fill in real values:

```bash
cp orchestrator/.env.example orchestrator/.env
cp frontend/.env.example frontend/.env
```

Key variables to set:

| Variable | Where | Purpose |
|---|---|---|
| `API_KEY` | `orchestrator/.env` | Shared secret the frontend uses to call the orchestrator |
| `OPENAI_API_KEY` | `query_agent/.env` | Required for the LLM fallback in constraint extraction |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | `frontend/.env` | Google OAuth login credentials |
| `ORCHESTRATOR_URL`, `ORCHESTRATOR_API_KEY` | `frontend/.env` | Where the frontend sends requests, and with which key |

> Confirm the exact variable names expected by `query_agent`'s LLM integration and `frontend/login.py`'s OAuth setup against the actual code — these were added after this README's initial draft.

## Running the Project

Start each service in its own terminal, in this order:

```bash
# Terminal 1 — Query Understanding Agent
cd query_agent && uvicorn query_agent:app --port 8001

# Terminal 2 — Retrieval Agent
cd retrieval_agent && uvicorn main:app --port 8002

# Terminal 3 — Review Analysis Agent
cd review_agent && uvicorn review_agent:app --port 8003

# Terminal 4 — Orchestrator (from the project root)
uvicorn orchestrator.main:app --port 8000

# Terminal 5 — Frontend
cd frontend && streamlit run login.py
```

Once all five are running:
- Orchestrator docs: **http://localhost:8000/docs**
- Frontend: **http://localhost:8501**


## Security Features

| Feature | Implementation |
|---|---|
| Authentication | API-key header (`X-API-Key`) required on the main query endpoint |
| User authentication | Google OAuth 2.0 — frontend reads only basic identity from the returned ID token; passwords are never processed |
| Input sanitization | Strips HTML/script tags, blocks SQL-injection-style payloads |
| Rate limiting | Caps requests per minute per client |
| Prompt-injection defense | Query validation blocks manipulation phrases (e.g. "ignore previous commands") before any agent sees them |
| LLM instruction-hierarchy defense | The Query Agent's LLM prompt treats user input strictly as data to extract from, never as instructions |
| Indirect injection resistance | Recommendation explanations are template-generated, not LLM-generated, so stored recipe/review text can never reach a prompt |
| Generic error responses | Orchestrator failures return fixed, generic error messages — never raw stack traces |
| Request timeouts | Every orchestrator → agent call has an explicit timeout |

## Responsible AI

- **Transparency:** every recommendation includes a `why_recommended` explanation and the raw scores behind it — no black-box ranking.
- **Privacy:** no personally identifying information is stored or logged by any agent; the orchestrator is stateless.
- **Fairness:** rule-based logic applies identically across all queries. Testing uncovered and fixed a real bug where the dairy-exclusion filter failed against actual ingredient names (e.g. "butter", "cream cheese") rather than the literal word "dairy" — verified with automated tests before submission.
- **Misuse prevention:** the system never gives medical advice; every response carries a disclaimer and directs users to a professional for medical/dietary decisions.

## Evaluation

Retrieval quality measured via Precision@5, Recall@5, and Mean Reciprocal Rank (MRR) on four manually labelled test queries:

| Query | Precision@5 | Recall@5 | MRR |
|---|---|---|---|
| Vegan chickpea curry dinner | 0.40 | 0.67 | 1.00 |
| High-protein egg breakfast | 0.60 | 0.75 | 1.00 |
| Vegetable pasta with tomato | 0.60 | 0.75 | 0.50 |
| Grilled chicken dinner | 0.60 | 0.75 | 1.00 |

A further query with weak dataset coverage (dairy-free fruit smoothie snack) produced markedly lower similarity scores (0.03–0.05) versus well-supported queries (0.13–0.34) — evidence the system correctly signals low confidence rather than returning confident but wrong matches.

## Testing

| Component | Test Type | Result |
|---|---|---|
| Query Agent | Unit tests (`test_query_agent.py`) | 8/8 passed |
| Retrieval Agent | Unit tests (`test_retrieval.py`) | 6/6 passed |
| Review Agent | Unit tests (`test_review_agent.py`) | 9/9 passed |
| Orchestrator | Unit tests (`test_orchestrator.py`) | 8/8 passed |
| Full pipeline | Manual end-to-end test | Passed — verified via Swagger docs and the Streamlit UI, using all four real agents (not mocks) |

## Contributors

| Name | Role | Student ID |
|---|---|---|
| S R M P T Rathnayake | Query Understanding Agent (NLP + LLM) | IT23642232 |
| K A G T N Waidyarathne | Recipe Retrieval & Nutrition Agent | IT23580176 |
| M D A K Mahagamage | Review Analysis Agent | IT23728844 |
| P A Tennakoon | Orchestrator, Recommendation Agent & Frontend | IT23599154 |


*This project was developed for IT3041 – Information Retrieval and Web Analytics. It is a prototype for educational purposes and does not provide medical or dietary advice.*