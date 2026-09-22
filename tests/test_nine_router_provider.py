import requests
import pytest

from app.config.settings import ConfigurationError, LLMSettings
from app.providers.base import LLMProviderError
from app.providers.factory import create_llm_provider
from app.providers.nine_router import NineRouterProvider


class FakeResponse:
    def __init__(self, body, status_code=200):
        self.body = body
        self.status_code = status_code

    def json(self):
        return self.body

    def raise_for_status(self):
        if self.status_code >= 400:
            error = requests.HTTPError("HTTP error")
            error.response = self
            raise error


class InvalidJsonResponse(FakeResponse):
    def json(self):
        raise ValueError("invalid json")


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


def provider(session):
    return NineRouterProvider(
        base_url="http://localhost:20128/v1",
        api_key="test-key",
        model="configured-model",
        timeout_seconds=30,
        session=session,
    )


def test_successful_generation():
    session = FakeSession(
        FakeResponse({"choices": [{"message": {"content": "Surabaya."}}]})
    )

    assert provider(session).generate([{"role": "user", "content": "Halo"}]) == "Surabaya."


def test_uses_configured_model_and_authorization_header():
    session = FakeSession(
        FakeResponse({"choices": [{"message": {"content": "Surabaya."}}]})
    )

    provider(session).generate([{"role": "user", "content": "Halo"}])

    url, kwargs = session.calls[0]
    assert url == "http://localhost:20128/v1/chat/completions"
    assert kwargs["json"]["model"] == "configured-model"
    assert kwargs["headers"]["Authorization"] == "Bearer test-key"
    assert kwargs["timeout"] == 30


def test_custom_model_override():
    session = FakeSession(
        FakeResponse({"choices": [{"message": {"content": "Surabaya."}}]})
    )

    provider(session).generate(
        [{"role": "user", "content": "Halo"}],
        model="override-model",
    )

    assert session.calls[0][1]["json"]["model"] == "override-model"


def test_http_error_becomes_provider_error():
    session = FakeSession(FakeResponse({"error": "bad request"}, status_code=400))

    with pytest.raises(LLMProviderError, match="status 400"):
        provider(session).generate([{"role": "user", "content": "Halo"}])


def test_network_error_becomes_provider_error():
    session = FakeSession(error=requests.Timeout("timeout"))

    with pytest.raises(LLMProviderError, match="9Router request failed"):
        provider(session).generate([{"role": "user", "content": "Halo"}])


@pytest.mark.parametrize("body", [{}, {"choices": []}])
def test_invalid_response_body_becomes_provider_error(body):
    session = FakeSession(FakeResponse(body))

    with pytest.raises(LLMProviderError, match="invalid response body"):
        provider(session).generate([{"role": "user", "content": "Halo"}])


@pytest.mark.parametrize("content", ["", "   ", None])
def test_empty_assistant_content_becomes_provider_error(content):
    session = FakeSession(
        FakeResponse({"choices": [{"message": {"content": content}}]})
    )

    with pytest.raises(LLMProviderError, match="empty assistant content"):
        provider(session).generate([{"role": "user", "content": "Halo"}])


def test_invalid_json_response_becomes_provider_error():
    session = FakeSession(InvalidJsonResponse(None))

    with pytest.raises(LLMProviderError, match="invalid response body"):
        provider(session).generate([{"role": "user", "content": "Halo"}])


def test_api_key_is_not_exposed_in_settings_repr():
    settings = LLMSettings(
        provider="9router",
        base_url="http://localhost:20128/v1",
        api_key="very-secret-key",
        model="test-model",
        timeout_seconds=60,
    )

    assert "very-secret-key" not in repr(settings)


def test_unsupported_provider_factory():
    settings = LLMSettings(
        provider="unknown",
        base_url="http://localhost:20128/v1",
        api_key="test-key",
        model="configured-model",
        timeout_seconds=30,
    )

    with pytest.raises(ConfigurationError, match="tidak didukung"):
        create_llm_provider(settings)
