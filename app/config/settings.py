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


@dataclass(frozen=True)
class MetabaseSettings:
    site_url: str
    embed_secret_key: str
    api_key: str
    username: str
    password: str
    timeout_seconds: int


def get_llm_settings(env_file: Path | None = None) -> LLMSettings:
    """Load LLM provider settings from the environment and optional .env file."""
    load_dotenv(env_file or ROOT_DIR / ".env")

    provider = _required("LLM_PROVIDER").strip().lower()
    model = _required("LLM_MODEL")
    timeout = _timeout_seconds()

    if provider == "ollama":
        base_url = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1").rstrip("/")
        api_key = os.getenv("LLM_API_KEY") or "ollama"
    elif provider == "groq":
        base_url = os.getenv(
            "LLM_BASE_URL", "https://api.groq.com/openai/v1"
        ).rstrip("/")
        api_key = _required("LLM_API_KEY")
    else:
        # Default untuk 9router dan provider OpenAI-compatible generik
        base_url = _required("LLM_BASE_URL").rstrip("/")
        api_key = _required("LLM_API_KEY")

    return LLMSettings(
        provider=provider,
        base_url=base_url,
        api_key=api_key,
        model=model,
        timeout_seconds=timeout,
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


def get_metabase_settings(env_file: Path | None = None) -> MetabaseSettings:
    load_dotenv(env_file or ROOT_DIR / ".env")
    return MetabaseSettings(
        site_url=_required("METABASE_SITE_URL").rstrip("/"),
        embed_secret_key=os.getenv("METABASE_EMBED_SECRET_KEY", ""),
        api_key=os.getenv("METABASE_API_KEY", ""),
        username=os.getenv("METABASE_USERNAME", ""),
        password=os.getenv("METABASE_PASSWORD", ""),
        timeout_seconds=_timeout_seconds(),
    )
