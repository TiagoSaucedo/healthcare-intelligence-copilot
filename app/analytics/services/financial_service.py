
import re
from typing import ClassVar

import pandas as pd

from app.analytics.services.common import (
    normalize_numeric_columns,
    safe_divide,
    safe_sum,
    validate_required_columns,
)
from app.database.repositories.financial_repository import (
    FinancialRepository,
)


class FinancialAnalyticsService:
    """
    Camada de serviços responsável pelas análises financeiras.
    """

    REQUIRED_COLUMNS: ClassVar[list[str]] = [
        "receita_competencia",
        "despesa_apresentada_atendimento",
        "despesa_paga_pagamento",
    ]

    def __init__(
        self,
        repository: FinancialRepository | None = None,
    ):
        self.repository = repository or FinancialRepository()

    @staticmethod
    def _validate_period(
        start_month: str,
        end_month: str,
    ) -> None:
        """Valida o formato e a sequência do período informado."""

        pattern = r"^\d{4}-(0[1-9]|1[0-2])$"

        for month in (start_month, end_month):
            if not isinstance(month, str) or not re.fullmatch(
                pattern, month
            ):
                raise ValueError(
                    "O período deve utilizar o formato YYYY-MM."
                )

        if start_month > end_month:
            raise ValueError(
                "O mês inicial não pode ser posterior ao final."
            )

    def get_monthly_overview(self) -> pd.DataFrame:
        """Retorna a visão financeira mensal completa."""

        return self.repository.get_monthly_overview()

    def get_monthly_overview_by_period(
        self,
        start_month: str,
        end_month: str,
    ) -> pd.DataFrame:
        """Retorna a visão financeira mensal filtrada por período."""

        self._validate_period(start_month, end_month)

        return self.repository.get_monthly_overview_by_period(
            start_month=start_month,
            end_month=end_month,
        )

    def get_financial_summary(
        self,
        start_month: str,
        end_month: str,
    ) -> dict:
        """Consolida os principais indicadores financeiros."""

        df = self.get_monthly_overview_by_period(
            start_month=start_month,
            end_month=end_month,
        )

        if df.empty:
            return {
                "periodo_inicial": start_month,
                "periodo_final": end_month,
                "quantidade_meses": 0,
                "receita_total": 0.0,
                "despesa_apresentada_total": 0.0,
                "despesa_paga_total": 0.0,
                "relacao_apresentada_receita_pct": None,
                "relacao_paga_receita_pct": None,
            }

        validate_required_columns(df, self.REQUIRED_COLUMNS)

        df = normalize_numeric_columns(
            df,
            self.REQUIRED_COLUMNS,
        )

        receita_total = safe_sum(df["receita_competencia"])
        despesa_apresentada = safe_sum(
            df["despesa_apresentada_atendimento"]
        )
        despesa_paga = safe_sum(
            df["despesa_paga_pagamento"]
        )

        relacao_apresentada = safe_divide(
            despesa_apresentada,
            receita_total,
        )
        relacao_paga = safe_divide(
            despesa_paga,
            receita_total,
        )

        return {
            "periodo_inicial": start_month,
            "periodo_final": end_month,
            "quantidade_meses": len(df),
            "receita_total": (
                round(receita_total, 2)
                if receita_total is not None
                else None
            ),
            "despesa_apresentada_total": (
                round(despesa_apresentada, 2)
                if despesa_apresentada is not None
                else None
            ),
            "despesa_paga_total": (
                round(despesa_paga, 2)
                if despesa_paga is not None
                else None
            ),
            "relacao_apresentada_receita_pct": (
                round(relacao_apresentada * 100, 2)
                if relacao_apresentada is not None
                else None
            ),
            "relacao_paga_receita_pct": (
                round(relacao_paga * 100, 2)
                if relacao_paga is not None
                else None
            ),
        }
