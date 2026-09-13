"""
Automated tests for the orchestrator.

These do NOT require the mock agent servers to be running - the calls to
query_agent / retrieval_agent / review_agent are patched directly, so this
suite tests the orchestrator's own logic (routing, security, merging) in
isolation. Run with:

    pytest orchestrator/tests -v
"""
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from orchestrator.config import settings
from orchestrator.main import app
from orchestrator.schemas import (
    ParsedConstraints,
    RetrievalResponse,
    RetrievedRecipe,
    ReviewAgentResponse,
    ReviewInsight,
)

client = TestClient(app)
AUTH_HEADERS = {"X-API-Key": settings.API_KEY}


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_query_without_api_key_is_rejected():
    # FastAPI rejects this at request-validation time (missing required
    # header) before our auth dependency even runs, hence 422 not 401 -
    # either way, the request never reaches the pipeline.
    response = client.post("/api/v1/query", json={"query": "vegan dinner"})
    assert response.status_code == 422


def test_query_with_wrong_api_key_is_rejected():
    response = client.post(
        "/api/v1/query", json={"query": "vegan dinner"}, headers={"X-API-Key": "wrong-key"}
    )
    assert response.status_code == 401


def test_blank_query_is_rejected():
    response = client.post("/api/v1/query", json={"query": "  "}, headers=AUTH_HEADERS)
    assert response.status_code == 422


def test_sql_injection_style_input_is_rejected():
    malicious = "dinner ideas; DROP TABLE users;"
    response = client.post("/api/v1/query", json={"query": malicious}, headers=AUTH_HEADERS)
    assert response.status_code == 400


@patch("orchestrator.routers.query.review_agent_client.analyze", new_callable=AsyncMock)
@patch("orchestrator.routers.query.retrieval_agent_client.search", new_callable=AsyncMock)
@patch("orchestrator.routers.query.query_agent_client.parse_query", new_callable=AsyncMock)
def test_full_pipeline_merges_results_correctly(mock_parse, mock_search, mock_analyze):
    mock_parse.return_value = ParsedConstraints(
        intent="recommend_recipe", diet_tags=["vegan"], max_calories=500
    )
    mock_search.return_value = RetrievalResponse(
        results=[
            RetrievedRecipe(
                recipe_id="r2",
                title="Tofu Stir Fry",
                score=0.9,
                calories=410,
                protein_g=22,
                diet_tags=["vegan"],
            )
        ]
    )
    mock_analyze.return_value = ReviewAgentResponse(
        insights=[
            ReviewInsight(
                recipe_id="r2",
                sentiment_score=0.4,
                sentiment_label="positive",
                aspects={"texture": "mixed"},
                summary="Good flavor overall.",
            )
        ]
    )

    response = client.post(
        "/api/v1/query",
        json={"query": "vegan dinner under 500 calories"},
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["recommendations"][0]["recipe_id"] == "r2"
    assert data["recommendations"][0]["sentiment_label"] == "positive"
    assert "vegan" in data["recommendations"][0]["why_recommended"]
    assert "disclaimer" in data


@patch("orchestrator.routers.query.query_agent_client.parse_query", new_callable=AsyncMock)
def test_upstream_agent_unreachable_returns_503(mock_parse):
    mock_parse.side_effect = ConnectionError("query_agent is unreachable at http://localhost:8001")

    response = client.post(
        "/api/v1/query", json={"query": "vegan dinner"}, headers=AUTH_HEADERS
    )
    assert response.status_code == 503
