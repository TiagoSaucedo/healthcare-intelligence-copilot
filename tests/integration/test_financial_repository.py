
import pytest

from app.database.repositories.financial_repository import (
    FinancialRepository,
)


@pytest.fixture
def repository() -> FinancialRepository:
    return FinancialRepository()


def test_get_monthly_overview_returns_complete_history(repository):
    """Valida a consulta do histórico financeiro completo."""

    df = repository.get_monthly_overview()

    expected_columns = {
        "ano_mes",
        "receita_competencia",
        "despesa_apresentada_atendimento",
        "despesa_paga_pagamento",
        "relacao_apresentada_receita_pct",
        "relacao_paga_receita_pct",
    }

    assert not df.empty
    assert expected_columns.issubset(set(df.columns))
    assert len(df) == 60
    assert df["ano_mes"].is_monotonic_increasing


def test_monthly_overview_financial_reconciliation(repository):
    """Verifica se os valores consultados reconciliam com o banco."""

    df = repository.get_monthly_overview()

    assert df["receita_competencia"].sum() == pytest.approx(
        11_934_503.22, abs=0.01
    )

    assert df["despesa_apresentada_atendimento"].sum() == pytest.approx(
        9_015_167.93, abs=0.01
    )

    assert df["despesa_paga_pagamento"].sum() == pytest.approx(
        7_231_820.73, abs=0.01
    )


def test_get_monthly_overview_by_period(repository):
    """Valida a filtragem por período."""

    df = repository.get_monthly_overview_by_period(
        start_month="2024-01",
        end_month="2024-03",
    )

    assert len(df) == 3

    assert df["ano_mes"].tolist() == [
        "2024-01",
        "2024-02",
        "2024-03",
    ]


def test_get_monthly_overview_rejects_invalid_period(repository):
    """Impede consultas com período inicial posterior ao final."""

    with pytest.raises(ValueError):
        repository.get_monthly_overview_by_period(
            start_month="2025-01",
            end_month="2024-01",
        )
