"""Base contract for LLM providers."""

from abc import ABC, abstractmethod
from typing import Any

import requests


class LLMProviderError(RuntimeError):
    """Raised when an LLM provider cannot generate a valid response."""


class LLMProvider(ABC):
    """Stable interface for text generation providers."""

    @abstractmethod
    def generate(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
    ) -> str:
        """Generate assistant text from chat messages."""


class OpenAICompatibleProvider(LLMProvider):
    """Shared HTTP client for OpenAI-compatible ``/chat/completions`` endpoints."""

    #: Prefix used in error messages, e.g. "Ollama request failed".
    name = "LLM"

    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        api_key: str,
        timeout_seconds: int = 60,
        session: Any = requests,
        extra_payload: dict[str, Any] | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self._session = session
        self._extra_payload = extra_payload or {}

    def generate(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
    ) -> str:
        payload = {
            "model": model or self.model,
            "messages": messages,
            **self._extra_payload,
        }

        try:
            response = self._session.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
        except requests.HTTPError as exc:
            status_code = getattr(exc.response, "status_code", "unknown")
            raise LLMProviderError(
                f"{self.name} request failed with status {status_code}"
            ) from exc
        except requests.RequestException as exc:
            raise LLMProviderError(f"{self.name} request failed: {exc}") from exc

        return self._assistant_content(response)

    def _assistant_content(self, response: Any) -> str:
        try:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise LLMProviderError(
                f"{self.name} returned an invalid response body"
            ) from exc

        if not isinstance(content, str) or not content.strip():
            raise LLMProviderError(f"{self.name} returned empty assistant content")
        return content
