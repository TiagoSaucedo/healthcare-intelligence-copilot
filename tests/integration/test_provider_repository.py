
import pytest

from app.database.repositories.provider_repository import (
    ProviderRepository,
)


@pytest.fixture
def repository() -> ProviderRepository:
    return ProviderRepository()


def test_get_provider_overview_returns_data(repository):
    """Valida o retorno dos indicadores por prestador."""

    df = repository.get_provider_overview()

    expected_columns = {
        "ano_mes",
        "id_prestador",
        "codigo_prestador",
        "nome_prestador",
        "tipo_prestador",
        "especialidade",
        "cidade",
        "estado",
        "total_itens",
        "total_contas",
        "total_beneficiarios",
        "despesa_apresentada",
        "despesa_paga",
        "valor_medio_por_item",
        "valor_medio_por_conta",
    }

    assert not df.empty
    assert expected_columns.issubset(set(df.columns))


def test_provider_overview_reconciles_expenses(repository):
    """Verifica a reconciliação das despesas com a base financeira."""

    df = repository.get_provider_overview()

    assert df["despesa_apresentada"].sum() == pytest.approx(
        9_015_167.93, abs=0.01
    )

    assert df["despesa_paga"].sum() == pytest.approx(
        7_231_820.73, abs=0.01
    )

    assert df["id_prestador"].nunique() == 150


def test_get_provider_by_period(repository):
    """Valida a consulta por período."""

    df = repository.get_provider_by_period(
        start_month="2024-01",
        end_month="2024-03",
    )

    assert not df.empty
    assert df["ano_mes"].min() >= "2024-01"
    assert df["ano_mes"].max() <= "2024-03"


def test_get_provider_by_period_rejects_invalid_period(repository):
    """Impede consultas com período inválido."""

    with pytest.raises(ValueError):
        repository.get_provider_by_period(
            start_month="2025-01",
            end_month="2024-01",
        )
