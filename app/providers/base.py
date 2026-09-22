"""Base contract for LLM providers."""

from abc import ABC, abstractmethod


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
