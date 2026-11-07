
import pytest

from app.analytics.tools import (
    ANALYTICAL_TOOLS,
    get_contract_summary,
    get_financial_summary,
    get_procedure_summary,
    get_provider_summary,
)


START_MONTH = "2028-01"
END_MONTH = "2028-12"

EXPECTED_TOOL_NAMES = {
    "get_financial_summary",
    "get_provider_summary",
    "get_procedure_summary",
    "get_contract_summary",
    "get_expense_ranking",
    "get_ranking_summary",
}

ALL_TOOLS = [
    get_financial_summary,
    get_provider_summary,
    get_procedure_summary,
    get_contract_summary,
]


def test_all_analytical_tools_are_registered():
    registered_names = {tool.name for tool in ANALYTICAL_TOOLS}
    assert registered_names == EXPECTED_TOOL_NAMES


@pytest.mark.parametrize("tool", ALL_TOOLS)
def test_analytical_tools_return_expected_period(tool):
    result = tool.invoke(
        {
            "start_month": START_MONTH,
            "end_month": END_MONTH,
        }
    )

    assert result["periodo_inicial"] == START_MONTH
    assert result["periodo_final"] == END_MONTH


def test_financial_tool_returns_twelve_months():
    result = get_financial_summary.invoke(
        {
            "start_month": START_MONTH,
            "end_month": END_MONTH,
        }
    )

    assert result["quantidade_meses"] == 12


@pytest.mark.parametrize("tool", ALL_TOOLS)
def test_analytical_tools_reject_invalid_period(tool):
    with pytest.raises(ValueError):
        tool.invoke(
            {
                "start_month": "2028-13",
                "end_month": END_MONTH,
            }
        )


def test_financial_tool_returns_reconciled_totals():
    result = get_financial_summary.invoke(
        {
            "start_month": START_MONTH,
            "end_month": END_MONTH,
        }
    )

    assert result["receita_total"] == pytest.approx(4419364.75)
    assert result["despesa_apresentada_total"] == pytest.approx(3326864.19)
    assert result["despesa_paga_total"] == pytest.approx(2731812.12)


def test_provider_tool_returns_expected_provider_count():
    result = get_provider_summary.invoke(
        {
            "start_month": START_MONTH,
            "end_month": END_MONTH,
        }
    )

    assert result["quantidade_prestadores"] == 150


def test_procedure_tool_returns_expected_procedure_count():
    result = get_procedure_summary.invoke(
        {
            "start_month": START_MONTH,
            "end_month": END_MONTH,
        }
    )

    assert result["quantidade_procedimentos"] == 200


def test_contract_tool_returns_expected_contract_count():
    result = get_contract_summary.invoke(
        {
            "start_month": START_MONTH,
            "end_month": END_MONTH,
        }
    )

    assert result["quantidade_contratos"] == 50
