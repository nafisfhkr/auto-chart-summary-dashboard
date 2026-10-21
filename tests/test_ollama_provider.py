import pytest
import requests

from app.providers.base import LLMProviderError
from app.providers.ollama import OllamaProvider


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


def test_ollama_successful_generation():
    session = FakeSession(
        FakeResponse({"choices": [{"message": {"content": "Ringkasan inflasi Jatim dari Llama 3."}}]})
    )
    provider = OllamaProvider(
        base_url="http://localhost:11434/v1",
        model="llama3",
        timeout_seconds=30,
        session=session,
    )

    result = provider.generate([{"role": "user", "content": "Analisis data"}])

    assert result == "Ringkasan inflasi Jatim dari Llama 3."
    url, kwargs = session.calls[0]
    assert url == "http://localhost:11434/v1/chat/completions"
    assert kwargs["json"]["model"] == "llama3"
    assert kwargs["timeout"] == 30


def test_ollama_custom_model_override():
    session = FakeSession(
        FakeResponse({"choices": [{"message": {"content": "Hasil Qwen."}}]})
    )
    provider = OllamaProvider(
        base_url="http://localhost:11434/v1",
        model="llama3",
        session=session,
    )

    result = provider.generate([{"role": "user", "content": "Analisis data"}], model="qwen2.5:7b")

    assert result == "Hasil Qwen."
    assert session.calls[0][1]["json"]["model"] == "qwen2.5:7b"


def test_ollama_connection_error_raises_llm_provider_error():
    session = FakeSession(error=requests.ConnectionError("Failed to connect to localhost:11434"))
    provider = OllamaProvider(
        base_url="http://localhost:11434/v1",
        model="llama3",
        session=session,
    )

    with pytest.raises(LLMProviderError, match="Ollama request failed"):
        provider.generate([{"role": "user", "content": "Analisis data"}])


def test_ollama_http_error_raises_llm_provider_error():
    session = FakeSession(FakeResponse({"error": "model 'llama3' not found"}, status_code=404))
    provider = OllamaProvider(
        base_url="http://localhost:11434/v1",
        model="llama3",
        session=session,
    )

    with pytest.raises(LLMProviderError, match="status 404"):
        provider.generate([{"role": "user", "content": "Analisis data"}])


@pytest.mark.parametrize("invalid_body", [{}, {"choices": []}, {"choices": [{"message": {}}]}])
def test_ollama_invalid_response_body_raises_error(invalid_body):
    session = FakeSession(FakeResponse(invalid_body))
    provider = OllamaProvider(
        base_url="http://localhost:11434/v1",
        model="llama3",
        session=session,
    )

    with pytest.raises(LLMProviderError, match="invalid response body"):
        provider.generate([{"role": "user", "content": "Analisis data"}])
