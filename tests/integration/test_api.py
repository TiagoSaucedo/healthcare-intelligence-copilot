
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.api.main import app


class FakeAgent:
    def invoke(self, payload):
        return {
            "messages": [
                SimpleNamespace(content="Despesa total: R$ 3.326.864,19")
            ]
        }


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(
        "app.api.main.create_analytics_agent",
        FakeAgent,
    )

    with TestClient(app) as test_client:
        yield test_client


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "healthcare-intelligence-copilot",
    }


def test_chat_endpoint_success(client):
    response = client.post(
        "/api/v1/chat",
        json={"message": "Qual foi a despesa total em 2028?"},
    )

    assert response.status_code == 200
    assert response.json()["answer"] == (
        "Despesa total: R$ 3.326.864,19"
    )


def test_chat_endpoint_invalid_message(client):
    response = client.post(
        "/api/v1/chat",
        json={"message": "oi"},
    )

    assert response.status_code == 422


def test_chat_endpoint_agent_error(client):
    class BrokenAgent:
        def invoke(self, payload):
            raise RuntimeError("Erro interno de teste")

    client.app.state.analytics_agent = BrokenAgent()

    response = client.post(
        "/api/v1/chat",
        json={"message": "Qual foi a despesa total em 2028?"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "Não foi possível processar a pergunta."
    )
