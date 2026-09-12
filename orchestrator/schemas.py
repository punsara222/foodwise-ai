"""
THE CONTRACT.

Every teammate should read this file first. It defines the exact JSON shape
that the orchestrator sends to / expects back from each agent. As long as
Punsara, Nithya and Ashani's real services accept and return JSON matching
these shapes, they can drop straight in and replace the mock servers with
zero changes to orchestrator code.

  User            ->  POST /api/v1/query           {UserQueryRequest}
  Orchestrator    ->  query_agent   POST /parse     {"query": str}
  query_agent     ->  Orchestrator                  {ParsedConstraints}
  Orchestrator    ->  retrieval_agent POST /search   {ParsedConstraints}
  retrieval_agent ->  Orchestrator                  {RetrievalResponse}
  Orchestrator    ->  review_agent  POST /analyze   {"recipe_ids": [str]}
  review_agent    ->  Orchestrator                  {ReviewAgentResponse}
  Orchestrator    ->  User                          {FinalResponse}
"""
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# 1) What the end user sends to the orchestrator
# ---------------------------------------------------------------------------
class UserQueryRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)
    user_id: Optional[str] = None

    @field_validator("query")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("query cannot be blank")
        return v.strip()


# ---------------------------------------------------------------------------
# 2) Contract with query_agent (Punsara)
#    NLP: entity extraction, intent detection -> structured JSON constraints
# ---------------------------------------------------------------------------
class ParsedConstraints(BaseModel):
    intent: Literal["recommend_recipe", "review_lookup", "general"] = "recommend_recipe"
    diet_tags: List[str] = []            # e.g. ["vegan", "gluten-free"]
    exclude_ingredients: List[str] = []  # e.g. ["dairy", "peanuts"]
    max_calories: Optional[int] = None
    min_protein_g: Optional[int] = None
    meal_type: Optional[str] = None      # e.g. "dinner", "breakfast"
    keywords: List[str] = []
    target_recipe_name: Optional[str] = None  # used when intent == review_lookup


# ---------------------------------------------------------------------------
# 3) Contract with retrieval_agent (Nithya)
#    TF-IDF / cosine similarity search + metadata filtering
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


# ---------------------------------------------------------------------------
# 4) Contract with review_agent (Ashani)
#    Sentiment analysis, aspect extraction, review summarization
# ---------------------------------------------------------------------------
class ReviewInsight(BaseModel):
    recipe_id: str
    sentiment_score: float  # roughly -1.0 .. 1.0
    sentiment_label: Literal["positive", "neutral", "negative"]
    aspects: Dict[str, str] = {}  # e.g. {"texture": "positive", "taste": "mixed"}
    summary: str


class ReviewAgentResponse(BaseModel):
    insights: List[ReviewInsight]


# ---------------------------------------------------------------------------
# 5) What the orchestrator's Recommendation Agent returns to the user
# ---------------------------------------------------------------------------
class FinalRecommendation(BaseModel):
    recipe_id: str
    title: str
    match_score: float
    why_recommended: str
    calories: Optional[int] = None
    protein_g: Optional[int] = None
    review_summary: Optional[str] = None
    sentiment_label: Optional[str] = None


class FinalResponse(BaseModel):
    query: str
    parsed_constraints: ParsedConstraints
    recommendations: List[FinalRecommendation]
    disclaimer: str = (
        "FoodWise AI provides general nutrition suggestions, not medical advice. "
        "Please verify allergen information against product packaging and consult "
        "a qualified professional for medical or dietary decisions."
    )
