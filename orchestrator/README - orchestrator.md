# orchestrator/ — Patali's part

FastAPI backend for FoodWise AI: routing/coordination logic, the
**Recommendation Agent** (merges results into a final answer), and the
**security layer** (auth, input sanitization, rate limiting).

## What's in here

```
orchestrator/
├── main.py                    FastAPI app entrypoint
├── config.py                  Settings (agent URLs, API key, etc.)
├── schemas.py                 THE CONTRACT — data shapes every agent must match
├── security.py                Auth, input sanitization, rate limiting
├── recommendation_agent.py    Merges retrieval + review results, explains why
├── clients/                   HTTP clients that call the other 3 agents
│   ├── query_agent_client.py
│   ├── retrieval_agent_client.py
│   └── review_agent_client.py
├── routers/
│   ├── query.py                POST /api/v1/query — the main pipeline
│   └── health.py                GET /health
├── mocks/                      Stand-ins for teammates' agents (see below)
│   ├── mock_query_agent.py
│   ├── mock_retrieval_agent.py
│   ├── mock_review_agent.py
│   └── mock_data.py
├── tests/
│   └── test_orchestrator.py    Automated tests (mocked, no servers needed)
├── requirements.txt
├── .env.example
└── run_local_dev.sh            Starts mocks + orchestrator together
```

## Setup (one-time)

1. Make sure you're in the `foodwise-ai/` project root (the folder that
   contains `orchestrator/`, `query_agent/`, etc.).
2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate          # Windows: venv\Scripts\activate
   pip install -r orchestrator/requirements.txt
   ```
3. Copy the env file:
   ```bash
   cp orchestrator/.env.example orchestrator/.env
   ```
   The defaults work out of the box for local testing — nothing to edit yet.

## Running it

**Easiest — everything at once:**
```bash
bash orchestrator/run_local_dev.sh
```
This starts the 3 mock agents (ports 8001–8003) and the orchestrator
(port 8000). Press `Ctrl+C` to stop all of them.

**Manually, in 4 separate terminals** (useful while debugging one piece):
```bash
uvicorn orchestrator.mocks.mock_query_agent:app --port 8001
uvicorn orchestrator.mocks.mock_retrieval_agent:app --port 8002
uvicorn orchestrator.mocks.mock_review_agent:app --port 8003
uvicorn orchestrator.main:app --reload --port 8000
```

Once running, open **http://localhost:8000/docs** for interactive
Swagger UI — you can try the `/api/v1/query` endpoint from the browser.

## Testing your part

**Automated tests (no servers needed):**
```bash
pytest orchestrator/tests -v
```
These patch the agent calls directly, so they test the orchestrator's own
logic (auth, sanitization, rate limiting, merging) in isolation.

**Manual end-to-end test (with mock servers running):**
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -H "X-API-Key: foodwise-dev-key-change-me" \
  -d '{"query": "high-protein dinner under 500 calories, no dairy"}'
```

**Security checks:**
```bash
# Missing API key -> 422
curl -X POST http://localhost:8000/api/v1/query -H "Content-Type: application/json" -d '{"query":"vegan lunch"}'

# Wrong API key -> 401
curl -X POST http://localhost:8000/api/v1/query -H "Content-Type: application/json" -H "X-API-Key: wrong" -d '{"query":"vegan lunch"}'

# SQL-injection-style input -> 400, blocked
curl -X POST http://localhost:8000/api/v1/query -H "Content-Type: application/json" -H "X-API-Key: foodwise-dev-key-change-me" -d '{"query":"dinner; DROP TABLE users;"}'
```

## How teammates plug in (the contract)

Everything is defined in **`schemas.py`** — read it first. Summary:

| Agent | Owner | Endpoint | Request | Response |
|---|---|---|---|---|
| query_agent | Punsara | `POST /parse` | `{"query": "text"}` | `ParsedConstraints` |
| retrieval_agent | Nithya | `POST /search` | `ParsedConstraints` | `RetrievalResponse` |
| review_agent | Ashani | `POST /analyze` | `{"recipe_ids": ["r1","r2"]}` | `ReviewAgentResponse` |

As long as a teammate's real FastAPI service returns JSON matching the
shape in `schemas.py`, they can run it on the matching port and the
orchestrator will use it automatically — **no orchestrator code changes
needed.** They should also each add a `GET /health` route (see the mocks
for an example) — good practice and useful for debugging.

To switch from a mock to someone's real service, only `.env` changes,
e.g.:
```
QUERY_AGENT_URL=http://localhost:8001   # -> Punsara's real query_agent
```

## Responsible AI in this part

- **Transparency**: every recommendation includes a `why_recommended`
  plain-language explanation instead of a black-box ranked list
  (`recommendation_agent.py`).
- **Privacy/Security**: input sanitization strips HTML/script tags and
  blocks SQL-injection-style payloads; API-key auth gates the endpoint;
  rate limiting prevents abuse (`security.py`).
- **Misuse prevention**: every response carries a disclaimer that this is
  not medical advice and to verify allergen info independently
  (`schemas.py::FinalResponse.disclaimer`).

## Notes for the frontend (whoever builds Streamlit later)

Call `POST http://localhost:8000/api/v1/query` with header
`X-API-Key: <the key from .env>` and body `{"query": "<user's text>"}`.
The response (`FinalResponse` in `schemas.py`) has everything needed to
render: a list of recommendations, each with title, scores, calories,
protein, a review summary, and a plain-language reason — plus the
disclaimer to show somewhere on screen.
