
import pandas as pd

import app.analytics.tools as analytics_tools


def test_expense_ranking_returns_analysis_and_passes_parameters(
    monkeypatch,
):
    expected_data = pd.DataFrame(
        [
            {
                "ranking": 1,
                "id_entidade": 48,
                "nome_entidade": "Central Assistência Médica 048",
                "quantidade_itens": 372,
                "quantidade_contas": 370,
                "valor_despesa": 77235.12,
                "participacao_pct": 2.32,
            },
            {
                "ranking": 2,
                "id_entidade": 92,
                "nome_entidade": "Prime Centro Médico 092",
                "quantidade_itens": 381,
                "quantidade_contas": 377,
                "valor_despesa": 75360.01,
                "participacao_pct": 2.27,
            },
        ]
    )

    expected_result = {
        "dimensao": "prestador",
        "metrica": "apresentada",
        "periodo_inicial": "2028-01",
        "periodo_final": "2028-12",
        "quantidade_entidades_total": 150,
        "quantidade_entidades_retornadas": 2,
        "valor_total_dimensao": 333000.0,
        "valor_total_top_n": 152595.13,
        "participacao_conjunta_pct": 45.82,
        "resultados": expected_data.to_dict(orient="records"),
    }

    received = {}

    def fake_get_ranking_analysis(**kwargs):
        received.update(kwargs)
        return expected_result

    monkeypatch.setattr(
        analytics_tools.ranking_service,
        "get_ranking_analysis",
        fake_get_ranking_analysis,
    )

    result = analytics_tools.get_expense_ranking.invoke(
        {
            "dimension": "prestador",
            "start_month": "2028-01",
            "end_month": "2028-12",
            "limit": 2,
            "metric": "apresentada",
        }
    )

    assert result == expected_result

    assert received == {
        "dimension": "prestador",
        "start_month": "2028-01",
        "end_month": "2028-12",
        "limit": 2,
        "metric": "apresentada",
    }


def test_ranking_summary_returns_expected_data(monkeypatch):
    expected_data = {
        "dimensao": "prestador",
        "metrica": "apresentada",
        "periodo_inicial": "2028-01",
        "periodo_final": "2028-12",
        "quantidade_entidades": 150,
        "quantidade_itens": 17158,
        "quantidade_contas": 17036,
        "valor_total": 3326864.19,
    }

    received = {}

    def fake_get_ranking_summary(**kwargs):
        received.update(kwargs)
        return expected_data

    monkeypatch.setattr(
        analytics_tools.ranking_service,
        "get_ranking_summary",
        fake_get_ranking_summary,
    )

    result = analytics_tools.get_ranking_summary.invoke(
        {
            "dimension": "prestador",
            "start_month": "2028-01",
            "end_month": "2028-12",
            "metric": "apresentada",
        }
    )

    assert result == expected_data

    assert received == {
        "dimension": "prestador",
        "start_month": "2028-01",
        "end_month": "2028-12",
        "metric": "apresentada",
    }


def test_expense_ranking_returns_empty_analysis(monkeypatch):
    expected_result = {
        "dimensao": "prestador",
        "metrica": "apresentada",
        "periodo_inicial": "2024-01",
        "periodo_final": "2024-01",
        "quantidade_entidades_total": 0,
        "quantidade_entidades_retornadas": 0,
        "valor_total_dimensao": 0.0,
        "valor_total_top_n": 0.0,
        "participacao_conjunta_pct": 0.0,
        "resultados": [],
    }

    monkeypatch.setattr(
        analytics_tools.ranking_service,
        "get_ranking_analysis",
        lambda **kwargs: expected_result,
    )

    result = analytics_tools.get_expense_ranking.invoke(
        {
            "dimension": "prestador",
            "start_month": "2024-01",
            "end_month": "2024-01",
            "limit": 10,
            "metric": "apresentada",
        }
    )

    assert result == expected_result
