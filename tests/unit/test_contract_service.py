import pandas as pd
import pytest
from unittest.mock import Mock

from app.analytics.services.contract_service import (
    ContractAnalyticsService,
)


@pytest.fixture
def mock_repository():
    return Mock()


@pytest.fixture
def service(mock_repository):
    return ContractAnalyticsService(
        repository=mock_repository
    )


def test_get_contract_overview(service, mock_repository):
    """Valida o encaminhamento da consulta ao repositório."""

    expected_df = pd.DataFrame(
        {
            "id_contrato": [1],
            "codigo_contrato": ["CONT0001"],
        }
    )

    mock_repository.get_contract_overview.return_value = expected_df

    result = service.get_contract_overview()

    pd.testing.assert_frame_equal(result, expected_df)
    mock_repository.get_contract_overview.assert_called_once()


def test_get_contract_by_period(service, mock_repository):
    """Valida a consulta de contratos por período."""

    expected_df = pd.DataFrame(
        {
            "ano_mes": ["2028-01"],
            "id_contrato": [1],
            "valor_total_apresentado": [50_000.00],
        }
    )

    mock_repository.get_contract_by_period.return_value = expected_df

    result = service.get_contract_by_period(
        start_month="2028-01",
        end_month="2028-02",
    )

    pd.testing.assert_frame_equal(result, expected_df)

    mock_repository.get_contract_by_period.assert_called_once_with(
        start_month="2028-01",
        end_month="2028-02",
    )


def test_get_contract_by_period_rejects_invalid_month(service):
    """Rejeita meses fora do intervalo permitido."""

    with pytest.raises(ValueError):
        service.get_contract_by_period(
            start_month="2028-13",
            end_month="2028-12",
        )


def test_get_contract_by_period_rejects_invalid_format(service):
    """Rejeita períodos fora do formato YYYY-MM."""

    with pytest.raises(ValueError):
        service.get_contract_by_period(
            start_month="28-01",
            end_month="2028-12",
        )


def test_get_contract_by_period_rejects_reversed_period(service):
    """Rejeita períodos em ordem cronológica inválida."""

    with pytest.raises(ValueError):
        service.get_contract_by_period(
            start_month="2028-12",
            end_month="2028-01",
        )


def test_get_contract_summary(service, mock_repository):
    """Valida a consolidação dos indicadores por contrato."""

    mock_repository.get_contract_by_period.return_value = (
        pd.DataFrame(
            {
                "id_contrato": [1, 1, 2],
                "quantidade_itens": [100, 150, 250],
                "quantidade_contas": [40, 60, 100],
                "quantidade_beneficiarios": [30, 45, 80],
                "quantidade_procedimentos": [20, 25, 30],
                "valor_total_apresentado": [
                    20_000.00,
                    30_000.00,
                    50_000.00,
                ],
                "valor_total_pago": [
                    18_000.00,
                    27_000.00,
                    45_000.00,
                ],
            }
        )
    )

    result = service.get_contract_summary(
        start_month="2028-01",
        end_month="2028-02",
    )

    assert result["quantidade_contratos"] == 2
    assert result["quantidade_itens"] == 500
    assert result["quantidade_contas"] == 200
    assert result["quantidade_beneficiarios"] == 155
    assert result["quantidade_procedimentos"] == 75
    assert result["despesa_apresentada_total"] == 100_000.00
    assert result["despesa_paga_total"] == 90_000.00
    assert result["valor_medio_por_item"] == 200.00
    assert result["valor_medio_por_conta"] == 500.00


def test_get_contract_summary_returns_empty_period(
    service,
    mock_repository,
):
    """Valida o comportamento quando não existem dados no período."""

    mock_repository.get_contract_by_period.return_value = (
        pd.DataFrame(
            columns=[
                "id_contrato",
                "quantidade_itens",
                "quantidade_contas",
                "quantidade_beneficiarios",
                "quantidade_procedimentos",
                "valor_total_apresentado",
                "valor_total_pago",
            ]
        )
    )

    result = service.get_contract_summary(
        start_month="2028-01",
        end_month="2028-02",
    )

    assert result["quantidade_contratos"] == 0
    assert result["quantidade_itens"] == 0
    assert result["quantidade_contas"] == 0
    assert result["quantidade_beneficiarios"] == 0
    assert result["quantidade_procedimentos"] == 0
    assert result["despesa_apresentada_total"] == 0.0
    assert result["despesa_paga_total"] == 0.0
    assert result["valor_medio_por_item"] is None
    assert result["valor_medio_por_conta"] is None