
import pandas as pd
import pytest
from unittest.mock import Mock

from app.analytics.services.financial_service import (
    FinancialAnalyticsService,
)


@pytest.fixture
def mock_repository():
    return Mock()


@pytest.fixture
def service(mock_repository):
    return FinancialAnalyticsService(
        repository=mock_repository
    )


def test_get_monthly_overview(service, mock_repository):
    """Valida o encaminhamento da consulta ao repositório."""

    expected_df = pd.DataFrame(
        {
            "ano_mes": ["2028-01"],
            "receita_competencia": [100_000.00],
        }
    )

    mock_repository.get_monthly_overview.return_value = expected_df

    result = service.get_monthly_overview()

    pd.testing.assert_frame_equal(result, expected_df)
    mock_repository.get_monthly_overview.assert_called_once()


def test_get_monthly_overview_by_period(
    service,
    mock_repository,
):
    """Valida a consulta financeira por período."""

    expected_df = pd.DataFrame(
        {
            "ano_mes": ["2028-01", "2028-02"],
            "receita_competencia": [100_000.00, 120_000.00],
        }
    )

    mock_repository.get_monthly_overview_by_period.return_value = (
        expected_df
    )

    result = service.get_monthly_overview_by_period(
        start_month="2028-01",
        end_month="2028-02",
    )

    pd.testing.assert_frame_equal(result, expected_df)

    mock_repository.get_monthly_overview_by_period.assert_called_once_with(
        start_month="2028-01",
        end_month="2028-02",
    )


def test_get_monthly_overview_by_period_rejects_missing_month(
    service,
):
    """Valida a obrigatoriedade dos meses inicial e final."""

    with pytest.raises(ValueError):
        service.get_monthly_overview_by_period(
            start_month="",
            end_month="2028-12",
        )


def test_get_financial_summary(service, mock_repository):
    """Valida a consolidação dos indicadores financeiros."""

    mock_repository.get_monthly_overview_by_period.return_value = (
        pd.DataFrame(
            {
                "ano_mes": ["2028-01", "2028-02"],
                "receita_competencia": [100_000.00, 100_000.00],
                "despesa_apresentada_atendimento": [
                    80_000.00,
                    90_000.00,
                ],
                "despesa_paga_pagamento": [
                    60_000.00,
                    70_000.00,
                ],
            }
        )
    )

    result = service.get_financial_summary(
        start_month="2028-01",
        end_month="2028-02",
    )

    assert result["quantidade_meses"] == 2
    assert result["receita_total"] == 200_000.00
    assert result["despesa_apresentada_total"] == 170_000.00
    assert result["despesa_paga_total"] == 130_000.00
    assert result["relacao_apresentada_receita_pct"] == 85.00
    assert result["relacao_paga_receita_pct"] == 65.00


def test_get_financial_summary_returns_empty_period(
    service,
    mock_repository,
):
    """Valida o comportamento quando não existem dados no período."""

    mock_repository.get_monthly_overview_by_period.return_value = (
        pd.DataFrame(
            columns=[
                "ano_mes",
                "receita_competencia",
                "despesa_apresentada_atendimento",
                "despesa_paga_pagamento",
            ]
        )
    )

    result = service.get_financial_summary(
        start_month="2028-01",
        end_month="2028-02",
    )

    assert result["quantidade_meses"] == 0
    assert result["receita_total"] == 0.0
    assert result["despesa_apresentada_total"] == 0.0
    assert result["despesa_paga_total"] == 0.0
    assert result["relacao_apresentada_receita_pct"] is None
    assert result["relacao_paga_receita_pct"] is None


def test_get_monthly_overview_rejects_invalid_month(service):
    """Rejeita meses fora do intervalo permitido."""

    with pytest.raises(ValueError):
        service.get_monthly_overview_by_period(
            start_month="2028-13",
            end_month="2028-12",
        )


def test_get_monthly_overview_rejects_invalid_format(service):
    """Rejeita períodos fora do formato YYYY-MM."""

    with pytest.raises(ValueError):
        service.get_monthly_overview_by_period(
            start_month="28-01",
            end_month="2028-12",
        )


def test_get_monthly_overview_rejects_reversed_period(service):
    """Rejeita períodos em ordem cronológica inválida."""

    with pytest.raises(ValueError):
        service.get_monthly_overview_by_period(
            start_month="2028-12",
            end_month="2028-01",
        )
