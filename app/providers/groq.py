"""Groq Cloud OpenAI-compatible LLM provider."""

from typing import Any

import requests

from app.providers.base import OpenAICompatibleProvider


class GroqProvider(OpenAICompatibleProvider):
    """Generate text through Groq's high-speed cloud inference API."""

    name = "Groq"

    def __init__(
        self,
        *,
        base_url: str = "https://api.groq.com/openai/v1",
        api_key: str,
        model: str = "llama-3.1-70b-versatile",
        timeout_seconds: int = 45,
        session: Any = requests,
    ) -> None:
        if not api_key or not api_key.strip():
            raise ValueError("Groq api_key must not be empty")

        super().__init__(
            base_url=base_url,
            model=model,
            api_key=api_key.strip(),
            timeout_seconds=timeout_seconds,
            session=session,
            extra_payload={"temperature": 0.2},
        )
