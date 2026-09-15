"""
Central configuration for the orchestrator.
All values can be overridden via a .env file (see .env.example) or real
environment variables, without touching this file.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "FoodWise AI Orchestrator"
    ENV: str = "development"

    # URLs of teammates' agents. In local dev these point at the mock
    # servers in orchestrator/mocks/. Once Punsara / Nithya / Ashani have
    # real services running, just change these URLs (or the .env file) -
    # no other code changes are needed.
    QUERY_AGENT_URL: str = "http://localhost:8001"
    RETRIEVAL_AGENT_URL: str = "http://localhost:8002"
    REVIEW_AGENT_URL: str = "http://localhost:8003"

    # Security
    API_KEY: str = "foodwise-dev-key-change-me"
    RATE_LIMIT_PER_MINUTE: int = 30

    # Networking
    REQUEST_TIMEOUT_SECONDS: float = 8.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
