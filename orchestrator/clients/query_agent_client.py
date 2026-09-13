"""
HTTP client for Punsara's query_agent.
Contract: POST {QUERY_AGENT_URL}/parse  {"query": str}  -> ParsedConstraints
"""
import httpx

from ..config import settings
from ..schemas import ParsedConstraints


async def parse_query(query: str) -> ParsedConstraints:
    url = f"{settings.QUERY_AGENT_URL}/parse"
    async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT_SECONDS) as client:
        try:
            response = await client.post(url, json={"query": query})
            response.raise_for_status()
        except httpx.RequestError as exc:
            raise ConnectionError(f"query_agent is unreachable at {url}: {exc}") from exc
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(f"query_agent returned an error: {exc}") from exc

    return ParsedConstraints(**response.json())
