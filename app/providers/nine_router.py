"""9Router OpenAI-compatible LLM provider."""

from typing import Any

import requests

from app.providers.base import LLMProvider, LLMProviderError


class NineRouterProvider(LLMProvider):
    """Generate text through a local 9Router OpenAI-compatible endpoint."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        timeout_seconds: int = 60,
        session: Any = requests,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds
        self._session = session

    def generate(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
    ) -> str:
        payload = {
            "model": model or self.model,
            "messages": messages,
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
                f"9Router request failed with status {status_code}"
            ) from exc
        except requests.RequestException as exc:
            raise LLMProviderError(f"9Router request failed: {exc}") from exc

        return self._assistant_content(response)

    @staticmethod
    def _assistant_content(response: requests.Response) -> str:
        try:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise LLMProviderError("9Router returned an invalid response body") from exc

        if not isinstance(content, str) or not content.strip():
            raise LLMProviderError("9Router returned empty assistant content")
        return content
