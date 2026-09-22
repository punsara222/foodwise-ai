"""
review_agent.py — Ashani's part: Review Analysis Agent for FoodWise AI.

Handles sentiment analysis, aspect extraction, and review summarization.
Matches the contract in orchestrator/schemas.py exactly, so it can plug
straight into the orchestrator with zero changes on their end.
"""
from typing import Dict, List, Literal

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Data shapes — must match orchestrator/schemas.py
# ---------------------------------------------------------------------------
class AnalyzeRequest(BaseModel):
    """What the orchestrator sends us."""
    recipe_ids: List[str]


class ReviewInsight(BaseModel):
    """One recipe's worth of review analysis."""
    recipe_id: str
    sentiment_score: float
    sentiment_label: Literal["positive", "neutral", "negative"]
    aspects: Dict[str, str] = {}
    summary: str


class ReviewAgentResponse(BaseModel):
    """What we send back to the orchestrator."""
    insights: List[ReviewInsight]


# ---------------------------------------------------------------------------
# Data loading — reads reviews from the shared dataset
# ---------------------------------------------------------------------------
import os
import csv
from collections import defaultdict

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "foodwise_final_dataset.csv")

FALLBACK_REVIEWS = {
    "r1": [
        "This was absolutely delicious, my whole family loved it!",
        "A bit too salty for my taste, but the texture was great.",
        "Super easy to make and turned out perfectly on the first try.",
    ],
    "r2": [
        "Took way too long to cook and wasn't worth the effort.",
        "Great flavor overall, would definitely make again.",
        "Instructions were confusing but the result was tasty.",
    ],
}

_reviews_cache = None


def load_reviews_dataset() -> dict:
    """Loads all reviews from the shared dataset, grouped by RecipeId.
    Note: this file is ~82MB, so the first call may take a few seconds —
    after that it's cached in memory for the rest of the server's life."""
    if not os.path.exists(DATA_PATH):
        return FALLBACK_REVIEWS

    reviews_by_recipe = defaultdict(list)
    with open(DATA_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            recipe_id = row.get("RecipeId")
            text = row.get("Review")
            if recipe_id and text:
                reviews_by_recipe[str(recipe_id)].append(text)

    return dict(reviews_by_recipe) if reviews_by_recipe else FALLBACK_REVIEWS


def get_reviews_for_recipe(recipe_id: str) -> list:
    """Returns the list of review text strings for one recipe_id."""
    global _reviews_cache
    if _reviews_cache is None:
        _reviews_cache = load_reviews_dataset()
    return _reviews_cache.get(recipe_id, [])


# ---------------------------------------------------------------------------
# Sentiment analysis — scores how positive/negative a review is
# ---------------------------------------------------------------------------
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()


def analyze_sentiment(text: str) -> float:
    """Returns a score between -1.0 (very negative) and 1.0 (very positive)
    for a single piece of text."""
    return _analyzer.polarity_scores(text)["compound"]


def average_sentiment(reviews: list) -> float:
    """Average sentiment score across all reviews for one recipe."""
    if not reviews:
        return 0.0
    scores = [analyze_sentiment(r) for r in reviews]
    return sum(scores) / len(scores)


def sentiment_label(score: float) -> str:
    """Converts a numeric score into the 3-way label the contract expects."""
    if score >= 0.05:
        return "positive"
    if score <= -0.05:
        return "negative"
    return "neutral"


# ---------------------------------------------------------------------------
# Aspect extraction — finds what's said about taste/texture/difficulty
# ---------------------------------------------------------------------------
ASPECT_KEYWORDS = {
    "taste": [
        "taste", "flavor", "flavour", "delicious", "bland",
        "salty", "sweet", "spicy", "yummy",
    ],
    "texture": [
        "texture", "crunchy", "soft", "chewy", "mushy", "crispy", "moist",
    ],
    "difficulty": [
        "easy", "hard", "difficult", "simple", "complicated",
        "confusing", "quick", "time-consuming", "took too long",
    ],
}


def extract_aspects(reviews: list) -> dict:
    """For each aspect (taste/texture/difficulty), finds reviews that
    mention it and averages the sentiment of just those reviews."""
    aspect_scores = {aspect: [] for aspect in ASPECT_KEYWORDS}

    for review in reviews:
        lowered = review.lower()
        for aspect, keywords in ASPECT_KEYWORDS.items():
            if any(keyword in lowered for keyword in keywords):
                aspect_scores[aspect].append(analyze_sentiment(review))

    result = {}
    for aspect, scores in aspect_scores.items():
        if not scores:
            continue  # nobody mentioned this aspect — leave it out
        avg = sum(scores) / len(scores)
        if avg >= 0.05:
            result[aspect] = "positive"
        elif avg <= -0.05:
            result[aspect] = "negative"
        else:
            result[aspect] = "mixed"

    return result


# ---------------------------------------------------------------------------
# Summarization — builds a short summary from real review sentences
# ---------------------------------------------------------------------------
import re
from collections import Counter

_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "is", "was", "were", "to", "of",
    "in", "it", "this", "that", "for", "on", "with", "my", "i", "we", "you",
    "at", "be", "as", "so", "if",
}


def summarize_reviews(reviews: list, max_sentences: int = 2) -> str:
    """Returns a short summary built from the highest-scoring sentences
    across all reviews for one recipe. Every word comes from a real
    review — nothing is generated or invented."""
    if not reviews:
        return "No reviews available for this recipe yet."

    text = " ".join(reviews)
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]

    if len(sentences) <= max_sentences:
        return " ".join(sentences)

    words = re.findall(r"[a-zA-Z']+", text.lower())
    word_freq = Counter(w for w in words if w not in _STOPWORDS)

    def sentence_score(sentence: str) -> float:
        sentence_words = re.findall(r"[a-zA-Z']+", sentence.lower())
        if not sentence_words:
            return 0.0
        return sum(word_freq.get(w, 0) for w in sentence_words) / len(sentence_words)

    ranked = sorted(sentences, key=sentence_score, reverse=True)
    top_sentences = set(ranked[:max_sentences])

    ordered_summary = [s for s in sentences if s in top_sentences]
    return " ".join(ordered_summary)


# ---------------------------------------------------------------------------
# The FastAPI app — wires everything together
# ---------------------------------------------------------------------------
from fastapi import FastAPI

app = FastAPI(title="FoodWise AI - Review Analysis Agent")


@app.get("/health")
def health():
    """Lets teammates and the orchestrator check this service is alive."""
    return {"status": "ok", "agent": "review_agent"}


@app.post("/analyze", response_model=ReviewAgentResponse)
def analyze(request: AnalyzeRequest) -> ReviewAgentResponse:
    """
    For each recipe_id the orchestrator sends us:
      1. Look up its reviews from the dataset
      2. Score overall sentiment
      3. Break sentiment down by aspect (taste / texture / difficulty)
      4. Build a short, explainable summary
    """
    insights = []

    for recipe_id in request.recipe_ids:
        reviews = get_reviews_for_recipe(recipe_id)

        score = average_sentiment(reviews)
        label = sentiment_label(score)
        aspects = extract_aspects(reviews)
        summary = summarize_reviews(reviews)

        insights.append(
            ReviewInsight(
                recipe_id=recipe_id,
                sentiment_score=round(score, 3),
                sentiment_label=label,
                aspects=aspects,
                summary=summary,
            )
        )

    return ReviewAgentResponse(insights=insights)