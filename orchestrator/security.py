"""
Security layer for the orchestrator: authentication, input sanitization,
and rate limiting. This is the piece the assignment brief calls out under
"Security features (Ex- authentication, input sanitization, encryption)".

Kept deliberately dependency-light (no Redis, no external services) so it
runs anywhere for a student project / demo, while still doing the real job.
"""
import html
import re
import time
from collections import defaultdict, deque

from fastapi import Header, HTTPException, Request, status

from .config import settings

# ---------------------------------------------------------------------------
# Authentication
# Simple shared API key for the demo. Every protected request must include:
#   X-API-Key: <settings.API_KEY>
# This is intentionally simple (no OAuth/JWT) because the brief only
# requires a credible security layer, not production-grade auth. It is
# clearly swappable for JWT/OAuth later without touching route logic.
# ---------------------------------------------------------------------------
def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")) -> bool:
    if x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
        )
    return True


# ---------------------------------------------------------------------------
# Rate limiting
# In-memory sliding-window limiter, keyed by client IP. Good enough for a
# single-process demo/mid-eval; swap for slowapi + Redis if you deploy
# multiple workers later.
# ---------------------------------------------------------------------------
_request_log: dict[str, deque] = defaultdict(deque)


def rate_limiter(request: Request) -> None:
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    window_seconds = 60

    log = _request_log[client_ip]
    while log and now - log[0] > window_seconds:
        log.popleft()

    if len(log) >= settings.RATE_LIMIT_PER_MINUTE:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please slow down and try again shortly.",
        )

    log.append(now)


# ---------------------------------------------------------------------------
# Input sanitization
# Escapes HTML, strips script tags, blocks obvious SQL-injection-style
# payloads, and caps length. Applied to the raw user query before it is
# ever forwarded to another agent or an LLM prompt.
# ---------------------------------------------------------------------------
_SCRIPT_PATTERN = re.compile(r"<\s*script.*?>.*?<\s*/\s*script\s*>", re.IGNORECASE | re.DOTALL)
_SQL_PATTERN = re.compile(r"(--|;|/\*|\*/|xp_|union\s+select|drop\s+table)", re.IGNORECASE)
MAX_QUERY_LENGTH = 500


def sanitize_text(value: str) -> str:
    if value is None:
        return value

    cleaned = value.strip()
    cleaned = _SCRIPT_PATTERN.sub("", cleaned)
    cleaned = html.escape(cleaned)

    if _SQL_PATTERN.search(cleaned):
        raise ValueError("Input contains disallowed characters or patterns.")

    return cleaned[:MAX_QUERY_LENGTH]
