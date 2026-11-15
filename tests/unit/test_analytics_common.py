
import pandas as pd
import pytest

from app.analytics.services.common import (
    normalize_numeric_columns,
    safe_divide,
    safe_sum,
    validate_required_columns,
)


def test_validate_required_columns_success():
    df = pd.DataFrame({"receita": [100], "despesa": [80]})

    validate_required_columns(df, ["receita", "despesa"])


def test_validate_required_columns_rejects_missing_column():
    df = pd.DataFrame({"receita": [100]})

    with pytest.raises(
        ValueError,
        match="Colunas obrigatórias ausentes",
    ):
        validate_required_columns(df, ["receita", "despesa"])


def test_normalize_numeric_columns_preserves_missing_values():
    df = pd.DataFrame({"valor": ["100", None, "200"]})

    result = normalize_numeric_columns(df, ["valor"])

    assert result["valor"].iloc[0] == 100
    assert pd.isna(result["valor"].iloc[1])
    assert result["valor"].iloc[2] == 200
    assert df["valor"].iloc[0] == "100"


def test_normalize_numeric_columns_rejects_invalid_values():
    df = pd.DataFrame({"valor": ["100", "inválido"]})

    with pytest.raises(ValueError, match="não numéricos"):
        normalize_numeric_columns(df, ["valor"])


@pytest.mark.parametrize("value", [float("inf"), float("-inf")])
def test_normalize_numeric_columns_rejects_infinity(value):
    df = pd.DataFrame({"valor": [100, value]})

    with pytest.raises(ValueError, match="infinitos"):
        normalize_numeric_columns(df, ["valor"])


def test_normalize_numeric_columns_rejects_missing_column():
    df = pd.DataFrame({"receita": [100]})

    with pytest.raises(ValueError, match="ausente"):
        normalize_numeric_columns(df, ["despesa"])


def test_safe_sum_returns_total():
    assert safe_sum(pd.Series([10, 20, 30])) == 60.0


def test_safe_sum_ignores_missing_values():
    assert safe_sum(pd.Series([10, None, 20])) == 30.0


def test_safe_sum_returns_none_when_all_values_are_missing():
    assert safe_sum(pd.Series([None, None])) is None


def test_safe_sum_rejects_infinity():
    with pytest.raises(ValueError, match="infinitos"):
        safe_sum(pd.Series([10, float("inf")]))


@pytest.mark.parametrize(
    ("numerator", "denominator", "expected"),
    [
        (100, 20, 5.0),
        (0, 20, 0.0),
        (100, 0, None),
        (100, None, None),
        (None, 20, None),
        (float("inf"), 20, None),
        (100, float("inf"), None),
    ],
)
def test_safe_divide(numerator, denominator, expected):
    assert safe_divide(numerator, denominator) == expected
