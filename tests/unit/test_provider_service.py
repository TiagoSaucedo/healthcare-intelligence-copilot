import pandas as pd
import pytest
from unittest.mock import Mock

from app.analytics.services.provider_service import (
    ProviderAnalyticsService,
)


@pytest.fixture
def mock_repository():
    return Mock()


@pytest.fixture
def service(mock_repository):
    return ProviderAnalyticsService(
        repository=mock_repository
    )


def test_get_provider_overview(service, mock_repository):
    """Valida o encaminhamento da consulta ao repositório."""

    expected_df = pd.DataFrame(
        {
            "id_prestador": [1],
            "nome_prestador": ["Hospital Fictício"],
        }
    )

    mock_repository.get_provider_overview.return_value = expected_df

    result = service.get_provider_overview()

    pd.testing.assert_frame_equal(result, expected_df)
    mock_repository.get_provider_overview.assert_called_once()


def test_get_provider_by_period(service, mock_repository):
    """Valida a consulta de prestadores por período."""

    expected_df = pd.DataFrame(
        {
            "ano_mes": ["2028-01"],
            "id_prestador": [1],
            "despesa_apresentada": [50_000.00],
        }
    )

    mock_repository.get_provider_by_period.return_value = expected_df

    result = service.get_provider_by_period(
        start_month="2028-01",
        end_month="2028-02",
    )

    pd.testing.assert_frame_equal(result, expected_df)

    mock_repository.get_provider_by_period.assert_called_once_with(
        start_month="2028-01",
        end_month="2028-02",
    )


def test_get_provider_by_period_rejects_invalid_month(service):
    """Rejeita meses fora do intervalo permitido."""

    with pytest.raises(ValueError):
        service.get_provider_by_period(
            start_month="2028-13",
            end_month="2028-12",
        )


def test_get_provider_by_period_rejects_invalid_format(service):
    """Rejeita períodos fora do formato YYYY-MM."""

    with pytest.raises(ValueError):
        service.get_provider_by_period(
            start_month="28-01",
            end_month="2028-12",
        )


def test_get_provider_by_period_rejects_reversed_period(service):
    """Rejeita períodos em ordem cronológica inválida."""

    with pytest.raises(ValueError):
        service.get_provider_by_period(
            start_month="2028-12",
            end_month="2028-01",
        )


def test_get_provider_summary(service, mock_repository):
    """Valida a consolidação dos indicadores por prestador."""

    mock_repository.get_provider_by_period.return_value = (
        pd.DataFrame(
            {
                "id_prestador": [1, 1, 2],
                "total_itens": [100, 150, 250],
                "total_contas": [40, 60, 100],
                "total_beneficiarios": [30, 45, 80],
                "despesa_apresentada": [
                    20_000.00,
                    30_000.00,
                    50_000.00,
                ],
                "despesa_paga": [
                    18_000.00,
                    27_000.00,
                    45_000.00,
                ],
            }
        )
    )

    result = service.get_provider_summary(
        start_month="2028-01",
        end_month="2028-02",
    )

    assert result["quantidade_prestadores"] == 2
    assert result["quantidade_itens"] == 500
    assert result["quantidade_contas"] == 200
    assert result["quantidade_beneficiarios"] == 155
    assert result["despesa_apresentada_total"] == 100_000.00
    assert result["despesa_paga_total"] == 90_000.00
    assert result["valor_medio_por_item"] == 200.00
    assert result["valor_medio_por_conta"] == 500.00


def test_get_provider_summary_returns_empty_period(
    service,
    mock_repository,
):
    """Valida o comportamento quando não existem dados no período."""

    mock_repository.get_provider_by_period.return_value = (
        pd.DataFrame(
            columns=[
                "id_prestador",
                "total_itens",
                "total_contas",
                "total_beneficiarios",
                "despesa_apresentada",
                "despesa_paga",
            ]
        )
    )

    result = service.get_provider_summary(
        start_month="2028-01",
        end_month="2028-02",
    )

    assert result["quantidade_prestadores"] == 0
    assert result["quantidade_itens"] == 0
    assert result["quantidade_contas"] == 0
    assert result["quantidade_beneficiarios"] == 0
    assert result["despesa_apresentada_total"] == 0.0
    assert result["despesa_paga_total"] == 0.0
    assert result["valor_medio_por_item"] is None
    assert result["valor_medio_por_conta"] is None