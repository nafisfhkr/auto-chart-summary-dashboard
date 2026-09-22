"""Factory for selecting the configured LLM provider."""

from app.config.settings import ConfigurationError, LLMSettings, get_llm_settings
from app.providers.base import LLMProvider
from app.providers.nine_router import NineRouterProvider


def create_llm_provider(settings: LLMSettings | None = None) -> LLMProvider:
    """Create the LLM provider configured by LLM_PROVIDER."""
    settings = settings or get_llm_settings()
    provider = settings.provider.strip().lower()

    if provider in {"9router", "nine_router", "ninerouter"}:
        return NineRouterProvider(
            base_url=settings.base_url,
            api_key=settings.api_key,
            model=settings.model,
            timeout_seconds=settings.timeout_seconds,
        )

    raise ConfigurationError(f"LLM_PROVIDER tidak didukung: {settings.provider}")
