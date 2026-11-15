from unittest.mock import Mock

import pandas as pd
import pytest

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
    """Valida o encaminhamento da consulta ao repositÃ³rio."""

    expected_df = pd.DataFrame(
        {
            "id_prestador": [1],
            "nome_prestador": ["Hospital FictÃ­cio"],
        }
    )

    mock_repository.get_provider_overview.return_value = expected_df

    result = service.get_provider_overview()

    pd.testing.assert_frame_equal(result, expected_df)
    mock_repository.get_provider_overview.assert_called_once()


def test_get_provider_by_period(service, mock_repository):
    """Valida a consulta de prestadores por perÃ­odo."""

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
    """Rejeita perÃ­odos fora do formato YYYY-MM."""

    with pytest.raises(ValueError):
        service.get_provider_by_period(
            start_month="28-01",
            end_month="2028-12",
        )


def test_get_provider_by_period_rejects_reversed_period(service):
    """Rejeita perÃ­odos em ordem cronolÃ³gica invÃ¡lida."""

    with pytest.raises(ValueError):
        service.get_provider_by_period(
            start_month="2028-12",
            end_month="2028-01",
        )


def test_get_provider_summary(service, mock_repository):
    """Valida a consolidaÃ§Ã£o dos indicadores por prestador."""

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
    """Valida o comportamento quando nÃ£o existem dados no perÃ­odo."""

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


def test_get_provider_summary_preserves_missing_values(
    service,
    mock_repository,
):
    """Preserva valores ausentes sem convertÃª-los em zero."""

    mock_repository.get_provider_by_period.return_value = (
        pd.DataFrame(
            {
                "id_prestador": [1, 2],
                "total_itens": [100, 100],
                "total_contas": [40, 60],
                "total_beneficiarios": [30, 45],
                "despesa_apresentada": [None, float("nan")],
                "despesa_paga": [18_000.00, None],
            }
        )
    )

    result = service.get_provider_summary(
        start_month="2028-01",
        end_month="2028-02",
    )

    assert result["despesa_apresentada_total"] is None
    assert result["despesa_paga_total"] == 18_000.00
    assert result["valor_medio_por_item"] is None
    assert result["valor_medio_por_conta"] is None


def test_get_provider_summary_handles_zero_denominators(
    service,
    mock_repository,
):
    """Retorna None quando os denominadores das mÃ©dias sÃ£o zero."""

    mock_repository.get_provider_by_period.return_value = (
        pd.DataFrame(
            {
                "id_prestador": [1],
                "total_itens": [0],
                "total_contas": [0],
                "total_beneficiarios": [0],
                "despesa_apresentada": [1000.00],
                "despesa_paga": [800.00],
            }
        )
    )

    result = service.get_provider_summary(
        start_month="2028-01",
        end_month="2028-02",
    )

    assert result["valor_medio_por_item"] is None
    assert result["valor_medio_por_conta"] is None


@pytest.mark.parametrize(
    "infinite_value",
    [float("inf"), float("-inf")],
)
def test_get_provider_summary_rejects_infinite_values(
    service,
    mock_repository,
    infinite_value,
):
    """Rejeita valores infinitos nas mÃ©tricas."""

    mock_repository.get_provider_by_period.return_value = (
        pd.DataFrame(
            {
                "id_prestador": [1],
                "total_itens": [100],
                "total_contas": [40],
                "total_beneficiarios": [30],
                "despesa_apresentada": [infinite_value],
                "despesa_paga": [800.00],
            }
        )
    )

    with pytest.raises(ValueError, match="infinitos"):
        service.get_provider_summary(
            start_month="2028-01",
            end_month="2028-02",
        )


def test_get_provider_summary_rejects_missing_columns(
    service,
    mock_repository,
):
    """Rejeita DataFrames sem colunas obrigatÃ³rias."""

    mock_repository.get_provider_by_period.return_value = (
        pd.DataFrame(
            {
                "id_prestador": [1],
                "despesa_apresentada": [1000.00],
            }
        )
    )

    with pytest.raises(
        ValueError,
        match="Colunas obrigatórias ausentes",
    ):
        service.get_provider_summary(
            start_month="2028-01",
            end_month="2028-02",
        )

def test_get_paid_provider_overview(service, mock_repository):
    """Valida o encaminhamento da consulta financeira."""

    expected_df = pd.DataFrame(
        {"id_prestador": [1], "despesa_paga": [18000.00]}
    )
    mock_repository.get_paid_provider_overview.return_value = expected_df

    result = service.get_paid_provider_overview()

    pd.testing.assert_frame_equal(result, expected_df)
    mock_repository.get_paid_provider_overview.assert_called_once()


def test_get_paid_provider_by_period(service, mock_repository):
    """Valida a consulta financeira por perÃ­odo."""

    expected_df = pd.DataFrame(
        {"ano_mes": ["2028-01"], "despesa_paga": [18000.00]}
    )
    mock_repository.get_paid_provider_by_period.return_value = expected_df

    result = service.get_paid_provider_by_period("2028-01", "2028-02")

    pd.testing.assert_frame_equal(result, expected_df)
    mock_repository.get_paid_provider_by_period.assert_called_once_with(
        start_month="2028-01",
        end_month="2028-02",
    )


def test_get_paid_provider_by_period_rejects_invalid_period(service):
    """Rejeita perÃ­odo financeiro invÃ¡lido."""

    with pytest.raises(ValueError):
        service.get_paid_provider_by_period("2028-13", "2028-12")


def test_get_paid_provider_summary(service, mock_repository):
    """Valida a consolidaÃ§Ã£o dos pagamentos e das mÃ©dias."""

    mock_repository.get_paid_provider_by_period.return_value = pd.DataFrame(
        {
            "id_prestador": [1, 1, 2],
            "total_itens_pagos": [100, 150, 250],
            "total_contas_pagas": [40, 60, 100],
            "total_beneficiarios": [30, 45, 80],
            "despesa_paga": [18000.00, 27000.00, 45000.00],
        }
    )

    result = service.get_paid_provider_summary("2028-01", "2028-02")

    assert result["quantidade_prestadores"] == 2
    assert result["quantidade_itens_pagos"] == 500
    assert result["quantidade_contas_pagas_mes_acumulada"] == 200
    assert result["quantidade_beneficiarios_mes_acumulada"] == 155
    assert result["despesa_paga_total"] == 90000.00
    assert result["valor_medio_pago_por_item"] == 180.00
    assert result["valor_medio_pago_por_conta"] == 450.00


def test_get_paid_provider_summary_returns_empty_period(
    service,
    mock_repository,
):
    """Valida o comportamento sem pagamentos no perÃ­odo."""

    mock_repository.get_paid_provider_by_period.return_value = pd.DataFrame(
        columns=[
            "id_prestador",
            "total_itens_pagos",
            "total_contas_pagas",
            "total_beneficiarios",
            "despesa_paga",
        ]
    )

    result = service.get_paid_provider_summary("2028-01", "2028-02")

    assert result["quantidade_prestadores"] == 0
    assert result["quantidade_itens_pagos"] == 0
    assert result["quantidade_contas_pagas_mes_acumulada"] == 0
    assert result["quantidade_beneficiarios_mes_acumulada"] == 0
    assert result["despesa_paga_total"] == 0.0
    assert result["valor_medio_pago_por_item"] is None
    assert result["valor_medio_pago_por_conta"] is None


def test_get_paid_provider_summary_handles_zero_denominators(
    service,
    mock_repository,
):
    """Retorna None quando nÃ£o hÃ¡ itens ou contas pagos."""

    mock_repository.get_paid_provider_by_period.return_value = pd.DataFrame(
        {
            "id_prestador": [1],
            "total_itens_pagos": [0],
            "total_contas_pagas": [0],
            "total_beneficiarios": [0],
            "despesa_paga": [800.00],
        }
    )

    result = service.get_paid_provider_summary("2028-01", "2028-02")

    assert result["valor_medio_pago_por_item"] is None
    assert result["valor_medio_pago_por_conta"] is None
