
import math
from collections.abc import Iterable

import pandas as pd


def validate_required_columns(
    df: pd.DataFrame,
    required_columns: Iterable[str],
) -> None:
    """Valida a presença das colunas obrigatórias."""

    missing_columns = set(required_columns) - set(df.columns)

    if missing_columns:
        columns = ", ".join(sorted(missing_columns))
        raise ValueError(
            f"Colunas obrigatórias ausentes: {columns}."
        )


def normalize_numeric_columns(
    df: pd.DataFrame,
    columns: Iterable[str],
) -> pd.DataFrame:
    """
    Converte colunas para valores numéricos.

    Valores ausentes permanecem como NaN.
    Valores não numéricos e infinitos são rejeitados.
    """

    result = df.copy()

    for column in columns:
        if column not in result.columns:
            raise ValueError(
                f"Coluna obrigatória ausente: {column}."
            )

        try:
            result[column] = pd.to_numeric(
                result[column],
                errors="raise",
            )
        except (ValueError, TypeError) as exc:
            raise ValueError(
                f"A coluna '{column}' contém valores não numéricos."
            ) from exc

        values = result[column].dropna()

        if not values.map(
            lambda value: math.isfinite(float(value))
        ).all():
            raise ValueError(
                f"A coluna '{column}' contém valores infinitos."
            )

    return result


def safe_sum(series: pd.Series) -> float | None:
    """
    Soma valores numéricos válidos.

    Retorna None quando todos os valores estão ausentes.
    """

    values = normalize_numeric_columns(
        series.to_frame(name="value"),
        ["value"],
    )["value"].dropna()

    if values.empty:
        return None

    return float(values.sum())


def safe_divide(
    numerator: float | None,
    denominator: float | None,
) -> float | None:
    """Realiza divisão segura, sem gerar NaN ou infinito."""

    if numerator is None or denominator is None:
        return None

    numerator = float(numerator)
    denominator = float(denominator)

    if not math.isfinite(numerator):
        return None

    if not math.isfinite(denominator) or denominator == 0:
        return None

    result = numerator / denominator

    if not math.isfinite(result):
        return None

    return result
