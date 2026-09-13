"""
The Recommendation Agent.

This is Patali's second agent (alongside the orchestrator/routing logic).
It takes the retrieval_agent's ranked recipes and review_agent's sentiment
insights and merges them into a final, explainable answer for the user.

Responsible AI note (Transparency, per the mid-eval Responsible AI slide):
every recommendation includes a plain-language "why_recommended" reason
instead of being a black-box ranked list.
"""
from typing import List, Optional

from .schemas import FinalRecommendation, ParsedConstraints, ReviewInsight, RetrievedRecipe


def _build_why_recommended(recipe: RetrievedRecipe, constraints: ParsedConstraints) -> str:
    reasons: List[str] = []

    if constraints.max_calories and recipe.calories and recipe.calories <= constraints.max_calories:
        reasons.append(f"{recipe.calories} cal fits your under-{constraints.max_calories}-cal request")

    if constraints.min_protein_g and recipe.protein_g and recipe.protein_g >= constraints.min_protein_g:
        reasons.append(f"{recipe.protein_g}g protein meets your {constraints.min_protein_g}g+ goal")

    matched_diet = set(constraints.diet_tags) & set(recipe.diet_tags)
    if matched_diet:
        reasons.append(f"matches your {', '.join(sorted(matched_diet))} preference")

    if constraints.exclude_ingredients:
        reasons.append(f"avoids {', '.join(constraints.exclude_ingredients)} as requested")

    if not reasons:
        reasons.append("closest overall match to your search")

    return "Recommended because " + "; ".join(reasons) + "."


def merge_results(
    constraints: ParsedConstraints,
    retrieved: List[RetrievedRecipe],
    reviews: Optional[List[ReviewInsight]] = None,
    top_k: int = 5,
) -> List[FinalRecommendation]:
    """Combine retrieval ranking + review sentiment into final recommendations."""
    review_map = {r.recipe_id: r for r in (reviews or [])}
    ranked = sorted(retrieved, key=lambda r: r.score, reverse=True)[:top_k]

    final: List[FinalRecommendation] = []
    for recipe in ranked:
        insight = review_map.get(recipe.recipe_id)
        final.append(
            FinalRecommendation(
                recipe_id=recipe.recipe_id,
                title=recipe.title,
                match_score=round(recipe.score, 3),
                why_recommended=_build_why_recommended(recipe, constraints),
                calories=recipe.calories,
                protein_g=recipe.protein_g,
                review_summary=insight.summary if insight else None,
                sentiment_label=insight.sentiment_label if insight else None,
            )
        )
    return final
