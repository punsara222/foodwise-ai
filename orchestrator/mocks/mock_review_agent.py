"""
MOCK stand-in for Ashani's review_agent.

Run standalone on port 8003:
    uvicorn orchestrator.mocks.mock_review_agent:app --port 8003

Swap REVIEW_AGENT_URL to her real service once it exposes the same
POST /analyze contract (see schemas.py).
"""
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

from .mock_data import FAKE_REVIEWS

app = FastAPI(title="MOCK review_agent (stands in for Ashani's part)")


class ReviewRequestIn(BaseModel):
    recipe_ids: List[str]


@app.post("/analyze")
def analyze(payload: ReviewRequestIn):
    insights = []
    for recipe_id in payload.recipe_ids:
        data = FAKE_REVIEWS.get(recipe_id)
        if data:
            insights.append({"recipe_id": recipe_id, **data})
    return {"insights": insights}


@app.get("/health")
def health():
    return {"status": "ok", "service": "mock_review_agent"}
