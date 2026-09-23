"""
frontend/api_client.py

Thin wrapper around the orchestrator's HTTP API. Nothing UI-specific lives
here — just requests in, dicts/exceptions out — so it's easy to test or
swap frameworks later.
"""
import os

import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:8000")
API_KEY = os.getenv("ORCHESTRATOR_API_KEY", "foodwise-dev-key-change-me")
REQUEST_TIMEOUT = 20


class OrchestratorError(Exception):
    """A friendly, user-facing error message about talking to the backend."""


def check_health() -> bool:
    """Quick liveness check, used to show a status indicator in the UI."""
    try:
        response = requests.get(f"{ORCHESTRATOR_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False


def get_recommendations(query: str) -> dict:
    """
    Calls POST /api/v1/query on the orchestrator and returns the parsed
    JSON response (matches FinalResponse in orchestrator/schemas.py).
    Raises OrchestratorError with a friendly message on any failure.
    """
    try:
        response = requests.post(
            f"{ORCHESTRATOR_URL}/api/v1/query",
            headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
            json={"query": query},
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        raise OrchestratorError(
            "Couldn't reach the FoodWise AI backend. Make sure the orchestrator "
            "and agent services are running."
        ) from exc

    if response.status_code == 401:
        raise OrchestratorError(
            "The backend rejected the API key. Check ORCHESTRATOR_API_KEY in frontend/.env."
        )
    if response.status_code == 429:
        raise OrchestratorError("Too many requests right now — please wait a moment and try again.")
    if response.status_code == 400:
        detail = _safe_detail(response)
        raise OrchestratorError(detail or "That query couldn't be processed — try rephrasing it.")
    if response.status_code in (502, 503):
        raise OrchestratorError(
            "One of the AI agents (query / retrieval / review) is unreachable. "
            "Make sure all backend services are running."
        )

    response.raise_for_status()
    return response.json()


def _safe_detail(response: requests.Response) -> str:
    try:
        return response.json().get("detail", "")
    except ValueError:
        return ""
