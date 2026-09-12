"""
MOCK stand-in for Punsara's query_agent.

Run standalone on port 8001:
    uvicorn orchestrator.mocks.mock_query_agent:app --port 8001

This exists purely so Patali can test the orchestrator end-to-end before
query_agent/ has real code in it. Punsara's real service just needs to
expose the same POST /parse contract (see schemas.py) and this file can be
deleted / the QUERY_AGENT_URL swapped over.
"""
import re

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="MOCK query_agent (stands in for Punsara's part)")


class QueryIn(BaseModel):
    query: str


@app.post("/parse")
def parse(payload: QueryIn):
    text = payload.query.lower()

    diet_tags = [
        tag for tag in ["vegan", "vegetarian", "halal", "diabetic", "dairy-free", "gluten-free"]
        if tag in text or tag.replace("-", " ") in text
    ]

    exclude_ingredients = []
    if "no dairy" in text or "dairy-free" in text or "dairy free" in text:
        exclude_ingredients.append("dairy")

    max_calories = None
    cal_match = re.search(r"under (\d+)\s*cal", text)
    if cal_match:
        max_calories = int(cal_match.group(1))

    min_protein_g = 25 if ("high-protein" in text or "high protein" in text) else None

    intent = "recommend_recipe"
    if any(kw in text for kw in ["review", "texture", "say about", "what do people"]):
        intent = "review_lookup"

    meal_type = None
    for meal in ["breakfast", "lunch", "dinner", "snack"]:
        if meal in text:
            meal_type = meal
            break

    return {
        "intent": intent,
        "diet_tags": diet_tags,
        "exclude_ingredients": exclude_ingredients,
        "max_calories": max_calories,
        "min_protein_g": min_protein_g,
        "meal_type": meal_type,
        "keywords": text.split(),
        "target_recipe_name": None,
    }


@app.get("/health")
def health():
    return {"status": "ok", "service": "mock_query_agent"}
