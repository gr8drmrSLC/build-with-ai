"""
config.py — environment loading and typed settings.

All configuration comes from environment variables. This module is the
single source of truth for every setting in the application. Nothing
else should read os.environ directly.

Usage:
    from core.config import settings

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    guard = BudgetGuard(session_limit_usd=settings.session_budget_usd)
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _load_env() -> None:
    """Load .env from the project root (two levels above src/core/)."""
    root = Path(__file__).resolve().parent.parent.parent
    env_file = root / ".env"
    if env_file.exists():
        load_dotenv(env_file)


_load_env()


class Settings(BaseSettings):
    """
    Typed settings loaded from environment variables.

    Required variables must be set in .env or the environment.
    Optional variables have defaults that are safe for development.
    All variables are documented in .env.example.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # ignore unknown env vars — don't fail on them
    )

    # --- Anthropic ---

    anthropic_api_key: str = Field(
        ...,
        description="Anthropic API key. Required. Get from console.anthropic.com.",
    )

    # --- Model selection ---

    orchestrator_model: str = Field(
        default="claude-sonnet-4-6",
        description="Model for orchestration and planning tasks.",
    )

    executor_model: str = Field(
        default="claude-haiku-4-5-20251001",
        description="Model for atomic execution tasks. Cheaper — use by default.",
    )

    # --- Budget ---

    session_budget_usd: float = Field(
        default=5.00,
        description="Maximum spend per session in USD. Enforced by BudgetGuard.",
        gt=0,
    )

    per_call_budget_usd: float = Field(
        default=0.10,
        description="Maximum cost for a single API call before requiring confirmation.",
        gt=0,
    )

    per_call_token_limit: int = Field(
        default=50_000,
        description="Maximum tokens in a single API call before requiring confirmation.",
        gt=0,
    )

    # --- Rate limiting ---

    requests_per_minute: int = Field(
        default=20,
        description="Maximum API requests per minute across all calls.",
        gt=0,
    )

    # --- Logging ---

    log_level: str = Field(
        default="INFO",
        description="Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL.",
    )

    log_format: str = Field(
        default="json",
        description="Log format: 'json' for structured logging, 'text' for development.",
    )

    # --- AWS (optional — only required for projects using AWS) ---

    aws_region: str = Field(
        default="us-east-1",
        description="AWS region for all service calls.",
    )

    aws_access_key_id: str | None = Field(
        default=None,
        description="AWS access key ID. Leave unset to use instance role or ~/.aws/credentials.",
    )

    aws_secret_access_key: str | None = Field(
        default=None,
        description="AWS secret access key. Leave unset to use instance role.",
    )

    # --- Validators ---

    @field_validator("anthropic_api_key")
    @classmethod
    def _validate_api_key(cls, v: str) -> str:
        if not v.startswith("sk-ant-"):
            raise ValueError(
                "ANTHROPIC_API_KEY must start with 'sk-ant-'. "
                "Check your .env file or environment."
            )
        return v

    @field_validator("log_level")
    @classmethod
    def _validate_log_level(cls, v: str) -> str:
        valid = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in valid:
            raise ValueError(f"LOG_LEVEL must be one of {valid}, got '{v}'")
        return upper

    @field_validator("log_format")
    @classmethod
    def _validate_log_format(cls, v: str) -> str:
        valid = {"json", "text"}
        lower = v.lower()
        if lower not in valid:
            raise ValueError(f"LOG_FORMAT must be one of {valid}, got '{v}'")
        return lower


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return the singleton Settings instance.

    Cached after first call — environment is read once at startup,
    not on every import. Call get_settings.cache_clear() in tests
    to reset between test cases.
    """
    return Settings()


# Module-level singleton for convenience: `from core.config import settings`
settings = get_settings()
