"""
Main pipeline endpoint: this is the routing/coordination logic.

Flow:
  1. Sanitize the raw user query (security layer).
  2. Call query_agent -> structured ParsedConstraints.
  3. Call retrieval_agent -> ranked RetrievedRecipe list.
  4. Call review_agent -> sentiment/aspect ReviewInsight list.
  5. Recommendation Agent merges everything into the final, explainable
     FinalResponse returned to the user.
"""
from fastapi import APIRouter, Depends

from ..clients import query_agent_client, retrieval_agent_client, review_agent_client
from ..recommendation_agent import merge_results
from ..schemas import FinalResponse, UserQueryRequest
from ..security import rate_limiter, sanitize_text, verify_api_key

router = APIRouter(prefix="/api/v1", tags=["query"])


@router.post(
    "/query",
    response_model=FinalResponse,
    dependencies=[Depends(verify_api_key), Depends(rate_limiter)],
)
async def handle_query(payload: UserQueryRequest) -> FinalResponse:
    clean_query = sanitize_text(payload.query)

    # Step 1: NLP parsing (Punsara's agent)
    constraints = await query_agent_client.parse_query(clean_query)

    # Step 2: Retrieval (Nithya's agent)
    retrieval = await retrieval_agent_client.search(constraints)

    # Step 3: Review analysis (Ashani's agent) - only if we have candidates
    review_insights = []
    if retrieval.results:
        recipe_ids = [r.recipe_id for r in retrieval.results]
        review_response = await review_agent_client.analyze(recipe_ids)
        review_insights = review_response.insights

    # Step 4: Merge (Recommendation Agent - Patali)
    recommendations = merge_results(constraints, retrieval.results, review_insights)

    return FinalResponse(
        query=clean_query,
        parsed_constraints=constraints,
        recommendations=recommendations,
    )
