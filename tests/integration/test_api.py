
from types import SimpleNamespace

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.analytics.services.contract_service import ContractAnalyticsService
from app.analytics.services.procedure_service import ProcedureAnalyticsService
from app.analytics.services.provider_service import ProviderAnalyticsService
from app.analytics.services.ranking_service import RankingAnalyticsService
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
            raise RuntimeError('Erro interno de teste')

    client.app.state.analytics_agent = BrokenAgent()

    response = client.post(
        '/api/v1/chat',
        json={'message': 'Qual foi a despesa total em 2028?'},
    )

    assert response.status_code == 500
    assert response.json()['detail'] == 'Não foi possível processar a pergunta.'



def test_paid_provider_summary_endpoint(client, monkeypatch):
    def fake_summary(self, start_month, end_month):
        return {
            "periodo_inicial": start_month,
            "periodo_final": end_month,
            "despesa_paga_total": 2731812.12,
        }

    monkeypatch.setattr(
        ProviderAnalyticsService,
        "get_paid_provider_summary",
        fake_summary,
    )

    response = client.get(
        "/api/v1/analytics/providers/paid/summary",
        params={
            "start_month": "2028-01",
            "end_month": "2028-12",
        },
    )

    assert response.status_code == 200
    assert response.json()["despesa_paga_total"] == 2731812.12
    assert response.json()["periodo_inicial"] == "2028-01"


def test_paid_provider_monthly_endpoint(client, monkeypatch):
    def fake_monthly(self, start_month, end_month):
        return pd.DataFrame(
            [
                {
                    "ano_mes": "2028-01",
                    "nome_prestador": "Hospital Teste",
                    "despesa_paga": 100000.00,
                },
                {
                    "ano_mes": "2028-02",
                    "nome_prestador": "Hospital Teste",
                    "despesa_paga": 120000.00,
                },
            ]
        )

    monkeypatch.setattr(
        ProviderAnalyticsService,
        "get_paid_provider_by_period",
        fake_monthly,
    )

    response = client.get(
        "/api/v1/analytics/providers/paid/monthly",
        params={
            "start_month": "2028-01",
            "end_month": "2028-02",
        },
    )

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["despesa_paga"] == 100000.00


@pytest.mark.parametrize(
    "endpoint",
    [
        "/api/v1/analytics/providers/paid/summary",
        "/api/v1/analytics/providers/paid/monthly",
    ],
)
def test_paid_provider_endpoints_reject_invalid_period(client, endpoint):
    response = client.get(
        endpoint,
        params={
            "start_month": "2028-13",
            "end_month": "2028-12",
        },
    )

    assert response.status_code == 422


def test_procedure_summary_endpoint(client, monkeypatch):
    def fake_summary(self, start_month, end_month):
        return {
            "periodo_inicial": start_month,
            "periodo_final": end_month,
            "quantidade_procedimentos": 150,
            "despesa_apresentada_total": 250000.00,
            "despesa_paga_total": 200000.00,
        }

    monkeypatch.setattr(
        ProcedureAnalyticsService,
        "get_procedure_summary",
        fake_summary,
    )

    response = client.get(
        "/api/v1/analytics/procedures/summary",
        params={
            "start_month": "2028-01",
            "end_month": "2028-12",
        },
    )

    assert response.status_code == 200
    assert response.json()["quantidade_procedimentos"] == 150
    assert response.json()["despesa_apresentada_total"] == 250000.00


def test_procedure_monthly_endpoint(client, monkeypatch):
    def fake_monthly(self, start_month, end_month):
        return pd.DataFrame(
            [
                {
                    "ano_mes": "2028-01",
                    "codigo_procedimento": "10101012",
                    "descricao": "Consulta m?dica",
                    "despesa_apresentada": 100000.00,
                },
                {
                    "ano_mes": "2028-02",
                    "codigo_procedimento": "10101012",
                    "descricao": "Consulta m?dica",
                    "despesa_apresentada": 120000.00,
                },
            ]
        )

    monkeypatch.setattr(
        ProcedureAnalyticsService,
        "get_procedure_by_period",
        fake_monthly,
    )

    response = client.get(
        "/api/v1/analytics/procedures/monthly",
        params={
            "start_month": "2028-01",
            "end_month": "2028-02",
        },
    )

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["codigo_procedimento"] == "10101012"


@pytest.mark.parametrize(
    "endpoint",
    [
        "/api/v1/analytics/procedures/summary",
        "/api/v1/analytics/procedures/monthly",
    ],
)
def test_procedure_endpoints_reject_invalid_period(client, endpoint):
    response = client.get(
        endpoint,
        params={
            "start_month": "2028-13",
            "end_month": "2028-12",
        },
    )

    assert response.status_code == 422


def test_contract_summary_endpoint(client, monkeypatch):
    def fake_summary(self, start_month, end_month):
        return {
            "periodo_inicial": start_month,
            "periodo_final": end_month,
            "quantidade_contratos": 25,
            "quantidade_itens": 1500,
            "despesa_apresentada_total": 500000.00,
            "despesa_paga_total": 420000.00,
        }

    monkeypatch.setattr(
        ContractAnalyticsService,
        "get_contract_summary",
        fake_summary,
    )

    response = client.get(
        "/api/v1/analytics/contracts/summary",
        params={
            "start_month": "2028-01",
            "end_month": "2028-12",
        },
    )

    assert response.status_code == 200
    assert response.json()["quantidade_contratos"] == 25
    assert response.json()["despesa_apresentada_total"] == 500000.00


def test_contract_monthly_endpoint(client, monkeypatch):
    def fake_monthly(self, start_month, end_month):
        return pd.DataFrame(
            [
                {
                    "ano_mes": "2028-01",
                    "id_contrato": 1,
                    "codigo_contrato": "CTR001",
                    "modalidade": "Individual",
                    "valor_total_apresentado": 100000.00,
                    "valor_total_pago": 85000.00,
                },
                {
                    "ano_mes": "2028-02",
                    "id_contrato": 2,
                    "codigo_contrato": "CTR002",
                    "modalidade": "Coletivo",
                    "valor_total_apresentado": 120000.00,
                    "valor_total_pago": 100000.00,
                },
            ]
        )

    monkeypatch.setattr(
        ContractAnalyticsService,
        "get_contract_by_period",
        fake_monthly,
    )

    response = client.get(
        "/api/v1/analytics/contracts/monthly",
        params={
            "start_month": "2028-01",
            "end_month": "2028-02",
        },
    )

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["codigo_contrato"] == "CTR001"


@pytest.mark.parametrize(
    "endpoint",
    [
        "/api/v1/analytics/contracts/summary",
        "/api/v1/analytics/contracts/monthly",
    ],
)
def test_contract_endpoints_reject_invalid_period(client, endpoint):
    response = client.get(
        endpoint,
        params={
            "start_month": "2028-13",
            "end_month": "2028-12",
        },
    )

    assert response.status_code == 422




def test_ranking_endpoint_success(client, monkeypatch):
    def fake_ranking(
        self, dimension, start_month, end_month, limit=10,
        metric="apresentada",
    ):
        return pd.DataFrame(
            [
                {
                    "ranking": 1,
                    "id_entidade": 10,
                    "nome_entidade": "Hospital Teste",
                    "valor_despesa": 150000.00,
                }
            ]
        )

    monkeypatch.setattr(
        RankingAnalyticsService,
        "get_ranking",
        fake_ranking,
    )

    response = client.get(
        "/api/v1/analytics/rankings",
        params={
            "dimension": "prestador",
            "start_month": "2028-01",
            "end_month": "2028-12",
            "limit": 10,
            "metric": "apresentada",
        },
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["nome_entidade"] == "Hospital Teste"
    assert response.json()[0]["valor_despesa"] == 150000.00


def test_ranking_summary_endpoint_success(client, monkeypatch):
    def fake_summary(
        self, dimension, start_month, end_month,
        metric="apresentada",
    ):
        return {
            "dimensao": dimension,
            "metrica": metric,
            "periodo_inicial": start_month,
            "periodo_final": end_month,
            "quantidade_entidades": 25,
            "quantidade_itens": 1500,
            "quantidade_contas": 1200,
            "valor_total": 500000.00,
        }

    monkeypatch.setattr(
        RankingAnalyticsService,
        "get_ranking_summary",
        fake_summary,
    )

    response = client.get(
        "/api/v1/analytics/rankings/summary",
        params={
            "dimension": "prestador",
            "start_month": "2028-01",
            "end_month": "2028-12",
            "metric": "paga",
        },
    )

    assert response.status_code == 200
    assert response.json()["quantidade_entidades"] == 25
    assert response.json()["valor_total"] == 500000.00
    assert response.json()["metrica"] == "paga"


def test_ranking_analysis_endpoint_success(client, monkeypatch):
    def fake_analysis(
        self, dimension, start_month, end_month,
        limit=10, metric="apresentada",
    ):
        return {
            "dimensao": dimension,
            "metrica": metric,
            "periodo_inicial": start_month,
            "periodo_final": end_month,
            "quantidade_entidades_total": 25,
            "quantidade_entidades_retornadas": 10,
            "valor_total_dimensao": 500000.00,
            "valor_total_top_n": 300000.00,
            "participacao_conjunta_pct": 60.00,
            "resultados": [],
        }

    monkeypatch.setattr(
        RankingAnalyticsService,
        "get_ranking_analysis",
        fake_analysis,
    )

    response = client.get(
        "/api/v1/analytics/rankings/analysis",
        params={
            "dimension": "contrato",
            "start_month": "2028-01",
            "end_month": "2028-12",
            "limit": 10,
            "metric": "apresentada",
        },
    )

    assert response.status_code == 200
    assert response.json()["quantidade_entidades_total"] == 25
    assert response.json()["valor_total_top_n"] == 300000.00
    assert response.json()["participacao_conjunta_pct"] == 60.00


@pytest.mark.parametrize(
    "endpoint",
    [
        "/api/v1/analytics/rankings",
        "/api/v1/analytics/rankings/summary",
        "/api/v1/analytics/rankings/analysis",
    ],
)
def test_ranking_endpoints_reject_invalid_period(client, endpoint):
    response = client.get(
        endpoint,
        params={
            "dimension": "prestador",
            "start_month": "2028-13",
            "end_month": "2028-12",
        },
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "endpoint",
    [
        "/api/v1/analytics/rankings",
        "/api/v1/analytics/rankings/summary",
        "/api/v1/analytics/rankings/analysis",
    ],
)
def test_ranking_endpoints_reject_invalid_dimension(
    client, endpoint,
):
    response = client.get(
        endpoint,
        params={
            "dimension": "invalida",
            "start_month": "2028-01",
            "end_month": "2028-12",
        },
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "endpoint",
    [
        "/api/v1/analytics/rankings",
        "/api/v1/analytics/rankings/summary",
        "/api/v1/analytics/rankings/analysis",
    ],
)
def test_ranking_endpoints_reject_invalid_metric(client, endpoint):
    response = client.get(
        endpoint,
        params={
            "dimension": "prestador",
            "start_month": "2028-01",
            "end_month": "2028-12",
            "metric": "invalida",
        },
    )

    assert response.status_code == 422


@pytest.mark.parametrize("limit", [0, 101])
@pytest.mark.parametrize(
    "endpoint",
    [
        "/api/v1/analytics/rankings",
        "/api/v1/analytics/rankings/analysis",
    ],
)
def test_ranking_endpoints_reject_invalid_limit(
    client, endpoint, limit,
):
    response = client.get(
        endpoint,
        params={
            "dimension": "prestador",
            "start_month": "2028-01",
            "end_month": "2028-12",
            "limit": limit,
        },
    )

    assert response.status_code == 422
