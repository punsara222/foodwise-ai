"""
retrieval_agent/schemas.py

Local copy of the parts of the contract that concern the retrieval agent.
Must stay in sync with orchestrator/schemas.py — if Patali changes the
shape of ParsedConstraints or RetrievalResponse there, update it here too.
"""
from typing import List, Literal, Optional

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# What the orchestrator sends you (POST /search body)
# ---------------------------------------------------------------------------
class ParsedConstraints(BaseModel):
    intent: Literal["recommend_recipe", "review_lookup", "general"] = "recommend_recipe"
    diet_tags: List[str] = []
    exclude_ingredients: List[str] = []
    max_calories: Optional[int] = None
    min_protein_g: Optional[int] = None
    meal_type: Optional[str] = None
    keywords: List[str] = []
    target_recipe_name: Optional[str] = None


# ---------------------------------------------------------------------------
# What you send back to the orchestrator
# ---------------------------------------------------------------------------
class RetrievedRecipe(BaseModel):
    recipe_id: str
    title: str
    score: float
    calories: Optional[int] = None
    protein_g: Optional[int] = None
    diet_tags: List[str] = []
    ingredients: List[str] = []


class RetrievalResponse(BaseModel):
    results: List[RetrievedRecipe]
    query_echo: Optional[str] = None