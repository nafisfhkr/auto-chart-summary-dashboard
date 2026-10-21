"""Ollama local OpenAI-compatible LLM provider."""

from typing import Any

import requests

from app.providers.base import OpenAICompatibleProvider


class OllamaProvider(OpenAICompatibleProvider):
    """Generate text through a local Ollama OpenAI-compatible endpoint."""

    name = "Ollama"

    def __init__(
        self,
        *,
        base_url: str = "http://localhost:11434/v1",
        model: str = "llama3",
        api_key: str = "ollama",
        timeout_seconds: int = 120,
        session: Any = requests,
    ) -> None:
        super().__init__(
            base_url=base_url,
            model=model,
            api_key=api_key or "ollama",
            timeout_seconds=timeout_seconds,
            session=session,
            extra_payload={"stream": False},
        )
