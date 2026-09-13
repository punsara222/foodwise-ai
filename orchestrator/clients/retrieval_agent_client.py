"""
HTTP client for Nithya's retrieval_agent.
Contract: POST {RETRIEVAL_AGENT_URL}/search  {ParsedConstraints}  -> RetrievalResponse
"""
import httpx

from ..config import settings
from ..schemas import ParsedConstraints, RetrievalResponse


async def search(constraints: ParsedConstraints) -> RetrievalResponse:
    url = f"{settings.RETRIEVAL_AGENT_URL}/search"
    async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT_SECONDS) as client:
        try:
            response = await client.post(url, json=constraints.model_dump())
            response.raise_for_status()
        except httpx.RequestError as exc:
            raise ConnectionError(f"retrieval_agent is unreachable at {url}: {exc}") from exc
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(f"retrieval_agent returned an error: {exc}") from exc

    return RetrievalResponse(**response.json())
