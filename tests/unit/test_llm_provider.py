
import pytest

from app.llm.provider import get_chat_model


def test_get_chat_model_returns_ollama(monkeypatch):
    monkeypatch.setattr(
        "app.llm.provider.settings.llm_provider",
        "ollama",
    )

    model = get_chat_model()

    assert type(model).__name__ == "ChatOllama"


def test_get_chat_model_returns_openai(monkeypatch):
    monkeypatch.setattr(
        "app.llm.provider.settings.llm_provider",
        "openai",
    )
    monkeypatch.setattr(
        "app.llm.provider.settings.openai_api_key",
        "test-api-key",
    )

    model = get_chat_model()

    assert type(model).__name__ == "ChatOpenAI"


def test_openai_requires_api_key(monkeypatch):
    monkeypatch.setattr(
        "app.llm.provider.settings.llm_provider",
        "openai",
    )
    monkeypatch.setattr(
        "app.llm.provider.settings.openai_api_key",
        None,
    )

    with pytest.raises(
        ValueError,
        match="OPENAI_API_KEY não foi configurada",
    ):
        get_chat_model()


def test_unsupported_provider_raises_error(monkeypatch):
    monkeypatch.setattr(
        "app.llm.provider.settings.llm_provider",
        "unsupported",
    )

    with pytest.raises(
        ValueError,
        match="Provedor LLM não suportado",
    ):
        get_chat_model()
