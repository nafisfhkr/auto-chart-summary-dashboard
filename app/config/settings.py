"""Environment-backed application settings."""

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[2]


class ConfigurationError(RuntimeError):
    """Raised when required application configuration is missing or invalid."""


@dataclass(frozen=True)
class LLMSettings:
    """Settings required to create an LLM provider."""

    provider: str
    base_url: str
    api_key: str = field(repr=False)
    model: str
    timeout_seconds: int


def get_llm_settings(env_file: Path | None = None) -> LLMSettings:
    """Load LLM provider settings from the environment and optional .env file."""
    load_dotenv(env_file or ROOT_DIR / ".env")

    return LLMSettings(
        provider=_required("LLM_PROVIDER"),
        base_url=_required("LLM_BASE_URL").rstrip("/"),
        api_key=_required("LLM_API_KEY"),
        model=_required("LLM_MODEL"),
        timeout_seconds=_timeout_seconds(),
    )


def _required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ConfigurationError(f"{name} belum diisi")
    return value


def _timeout_seconds() -> int:
    raw_value = os.getenv("LLM_TIMEOUT_SECONDS", "60")
    try:
        timeout = int(raw_value)
    except ValueError as exc:
        raise ConfigurationError("LLM_TIMEOUT_SECONDS harus berupa angka") from exc
    if timeout <= 0:
        raise ConfigurationError("LLM_TIMEOUT_SECONDS harus lebih dari 0")
    return timeout
