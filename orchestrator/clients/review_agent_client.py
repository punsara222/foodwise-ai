"""
HTTP client for Ashani's review_agent.
Contract: POST {REVIEW_AGENT_URL}/analyze  {"recipe_ids": [str]}  -> ReviewAgentResponse
"""
from typing import List

import httpx

from ..config import settings
from ..schemas import ReviewAgentResponse


async def analyze(recipe_ids: List[str]) -> ReviewAgentResponse:
    url = f"{settings.REVIEW_AGENT_URL}/analyze"
    async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT_SECONDS) as client:
        try:
            response = await client.post(url, json={"recipe_ids": recipe_ids})
            response.raise_for_status()
        except httpx.RequestError as exc:
            raise ConnectionError(f"review_agent is unreachable at {url}: {exc}") from exc
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(f"review_agent returned an error: {exc}") from exc

    return ReviewAgentResponse(**response.json())
