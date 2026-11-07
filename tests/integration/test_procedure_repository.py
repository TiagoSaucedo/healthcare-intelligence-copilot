
import pytest

from app.database.repositories.procedure_repository import (
    ProcedureRepository,
)


@pytest.fixture
def repository() -> ProcedureRepository:
    return ProcedureRepository()


def test_get_procedure_overview_returns_data(repository):
    """Valida o retorno dos indicadores por procedimento."""

    df = repository.get_procedure_overview()

    expected_columns = {
        "ano_mes",
        "id_procedimento",
        "codigo_procedimento",
        "descricao",
        "grupo_procedimento",
        "categoria",
        "tipo_procedimento",
        "total_itens",
        "total_contas",
        "total_beneficiarios",
        "quantidade_total",
        "despesa_apresentada",
        "despesa_paga",
        "valor_medio_por_item",
        "valor_medio_por_unidade",
    }

    assert not df.empty
    assert expected_columns.issubset(set(df.columns))


def test_procedure_overview_reconciles_expenses(repository):
    """Verifica a reconciliação das despesas com a base financeira."""

    df = repository.get_procedure_overview()

    assert df["despesa_apresentada"].sum() == pytest.approx(
        9_015_167.93, abs=0.01
    )

    assert df["despesa_paga"].sum() == pytest.approx(
        7_231_820.73, abs=0.01
    )

    assert df["id_procedimento"].nunique() == 200


def test_get_procedure_by_period(repository):
    """Valida a consulta por período."""

    df = repository.get_procedure_by_period(
        start_month="2024-01",
        end_month="2024-03",
    )

    assert not df.empty
    assert df["ano_mes"].min() >= "2024-01"
    assert df["ano_mes"].max() <= "2024-03"


def test_get_procedure_by_period_rejects_invalid_period(repository):
    """Impede consultas com período inválido."""

    with pytest.raises(ValueError):
        repository.get_procedure_by_period(
            start_month="2025-01",
            end_month="2024-01",
        )
