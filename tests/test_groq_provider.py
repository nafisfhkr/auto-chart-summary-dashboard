import pytest
import requests

from app.providers.base import LLMProviderError
from app.providers.groq import GroqProvider


class FakeResponse:
    def __init__(self, body, status_code=200):
        self.body = body
        self.status_code = status_code

    def json(self):
        return self.body

    def raise_for_status(self):
        if self.status_code >= 400:
            error = requests.HTTPError(f"HTTP {self.status_code}")
            error.response = self
            raise error


class FakeSession:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if self.error:
            raise self.error
        return self.response


def test_groq_successful_generation():
    session = FakeSession(
        FakeResponse({"choices": [{"message": {"content": "Analisis cepat dari Groq."}}]})
    )
    provider = GroqProvider(
        base_url="https://api.groq.com/openai/v1",
        api_key="gsk_secret_123",
        model="llama-3.1-70b-versatile",
        timeout_seconds=30,
        session=session,
    )

    result = provider.generate([{"role": "user", "content": "Ringkas data"}])

    assert result == "Analisis cepat dari Groq."
    url, kwargs = session.calls[0]
    assert url == "https://api.groq.com/openai/v1/chat/completions"
    assert kwargs["headers"]["Authorization"] == "Bearer gsk_secret_123"
    assert kwargs["json"]["model"] == "llama-3.1-70b-versatile"


def test_groq_requires_api_key():
    with pytest.raises(ValueError, match="Groq api_key must not be empty"):
        GroqProvider(
            base_url="https://api.groq.com/openai/v1",
            api_key="",
            model="llama-3.1-70b-versatile",
        )


def test_groq_rate_limit_or_http_error():
    session = FakeSession(FakeResponse({"error": "rate limit exceeded"}, status_code=429))
    provider = GroqProvider(
        base_url="https://api.groq.com/openai/v1",
        api_key="gsk_secret_123",
        model="llama-3.1-70b-versatile",
        session=session,
    )

    with pytest.raises(LLMProviderError, match="status 429"):
        provider.generate([{"role": "user", "content": "Ringkas data"}])


def test_groq_network_timeout():
    session = FakeSession(error=requests.Timeout("Connection timed out to api.groq.com"))
    provider = GroqProvider(
        base_url="https://api.groq.com/openai/v1",
        api_key="gsk_secret_123",
        model="llama-3.1-70b-versatile",
        session=session,
    )

    with pytest.raises(LLMProviderError, match="Groq request failed"):
        provider.generate([{"role": "user", "content": "Ringkas data"}])
