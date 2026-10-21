"""9Router OpenAI-compatible LLM provider."""

from typing import Any

import requests

from app.providers.base import OpenAICompatibleProvider


class NineRouterProvider(OpenAICompatibleProvider):
    """Generate text through a local 9Router OpenAI-compatible endpoint."""

    name = "9Router"

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        timeout_seconds: int = 60,
        session: Any = requests,
    ) -> None:
        super().__init__(
            base_url=base_url,
            model=model,
            api_key=api_key,
            timeout_seconds=timeout_seconds,
            session=session,
        )
