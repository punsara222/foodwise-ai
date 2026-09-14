"""
MOCK stand-in for Nithya's retrieval_agent.

Run standalone on port 8002:
    uvicorn orchestrator.mocks.mock_retrieval_agent:app --port 8002

Swap RETRIEVAL_AGENT_URL to her real service once it exposes the same
POST /search contract (see schemas.py).
"""
from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel

from .mock_data import SAMPLE_RECIPES

app = FastAPI(title="MOCK retrieval_agent (stands in for Nithya's part)")


class ConstraintsIn(BaseModel):
    intent: str = "recommend_recipe"
    diet_tags: List[str] = []
    exclude_ingredients: List[str] = []
    max_calories: Optional[int] = None
    min_protein_g: Optional[int] = None
    meal_type: Optional[str] = None
    keywords: List[str] = []
    target_recipe_name: Optional[str] = None
    # Always populated by the orchestrator (see routers/query.py), even if
    # query_agent leaves it blank - this is the real text to vectorize.
    raw_query: Optional[str] = None


def _text_overlap_score(recipe: dict, constraints: "ConstraintsIn") -> float:
    """
    Crude placeholder for real TF-IDF + cosine similarity: scores a recipe
    by how many query words appear in its title/ingredients. Nithya's real
    retrieval_agent should replace this with an actual TF-IDF vectorizer
    fit over the recipe corpus (title + ingredients + description) and
    cosine similarity against a vector built from `raw_query` (falling
    back to `keywords` if she wants an extra signal on top).
    """
    query_text = (constraints.raw_query or " ".join(constraints.keywords) or "").lower()
    if not query_text:
        return 0.0
    query_words = set(query_text.split())
    recipe_words = set(recipe["title"].lower().split())
    for ingredient in recipe["ingredients"]:
        recipe_words.update(ingredient.lower().split())
    overlap = query_words & recipe_words
    return min(len(overlap) * 0.1, 0.3)


@app.post("/search")
def search(constraints: ConstraintsIn):
    results = []
    for recipe in SAMPLE_RECIPES:
        if constraints.exclude_ingredients and any(
            ing in recipe["ingredients"] for ing in constraints.exclude_ingredients
        ):
            continue

        score = 0.5
        if constraints.diet_tags and set(constraints.diet_tags) & set(recipe["diet_tags"]):
            score += 0.3
        if constraints.max_calories and recipe["calories"] <= constraints.max_calories:
            score += 0.15
        if constraints.min_protein_g and recipe["protein_g"] >= constraints.min_protein_g:
            score += 0.15
        score += _text_overlap_score(recipe, constraints)

        results.append({**recipe, "score": round(min(score, 1.0), 3)})

    results.sort(key=lambda r: r["score"], reverse=True)
    return {"results": results, "query_echo": constraints.raw_query}


@app.get("/health")
def health():
    return {"status": "ok", "service": "mock_retrieval_agent"}
