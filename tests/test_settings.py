import pytest

from app.config.settings import ConfigurationError, LLMSettings, get_llm_settings


ENV_NAMES = (
    "LLM_PROVIDER",
    "LLM_BASE_URL",
    "LLM_API_KEY",
    "LLM_MODEL",
    "LLM_TIMEOUT_SECONDS",
)


def clean_environment(monkeypatch):
    for name in ENV_NAMES:
        monkeypatch.delenv(name, raising=False)


def test_missing_required_settings_raise_configuration_error(monkeypatch, tmp_path):
    for missing_name in ENV_NAMES[:4]:
        clean_environment(monkeypatch)
        values = {
            "LLM_PROVIDER": "9router",
            "LLM_BASE_URL": "http://localhost:20128/v1",
            "LLM_API_KEY": "test-key",
            "LLM_MODEL": "test-model",
        }
        values.pop(missing_name)
        for name, value in values.items():
            monkeypatch.setenv(name, value)

        with pytest.raises(ConfigurationError):
            get_llm_settings(tmp_path / "empty.env")


@pytest.mark.parametrize("timeout", ["not-a-number", "0", "-1"])
def test_invalid_timeout_raises_configuration_error(monkeypatch, tmp_path, timeout):
    clean_environment(monkeypatch)
    monkeypatch.setenv("LLM_PROVIDER", "9router")
    monkeypatch.setenv("LLM_BASE_URL", "http://localhost:20128/v1")
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_MODEL", "test-model")
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", timeout)

    with pytest.raises(ConfigurationError):
        get_llm_settings(tmp_path / "empty.env")


def test_valid_configuration_is_loaded_and_normalized(monkeypatch, tmp_path):
    clean_environment(monkeypatch)
    monkeypatch.setenv("LLM_PROVIDER", "9router")
    monkeypatch.setenv("LLM_BASE_URL", "http://localhost:20128/v1/")
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_MODEL", "test-model")
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "45")

    settings = get_llm_settings(tmp_path / "empty.env")

    assert settings == LLMSettings(
        provider="9router",
        base_url="http://localhost:20128/v1",
        api_key="test-key",
        model="test-model",
        timeout_seconds=45,
    )


def test_timeout_defaults_to_60(monkeypatch, tmp_path):
    clean_environment(monkeypatch)
    monkeypatch.setenv("LLM_PROVIDER", "9router")
    monkeypatch.setenv("LLM_BASE_URL", "http://localhost:20128/v1")
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_MODEL", "test-model")

    settings = get_llm_settings(tmp_path / "empty.env")

    assert settings.timeout_seconds == 60
