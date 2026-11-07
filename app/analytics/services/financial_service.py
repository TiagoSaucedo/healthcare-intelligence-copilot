
import re

import pandas as pd

from app.database.repositories.financial_repository import (
    FinancialRepository,
)


class FinancialAnalyticsService:
    """
    Camada de serviços responsável pelas análises financeiras.
    """

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

        receita_total = df["receita_competencia"].sum()
        despesa_apresentada = (
            df["despesa_apresentada_atendimento"].sum()
        )
        despesa_paga = df["despesa_paga_pagamento"].sum()

        return {
            "periodo_inicial": start_month,
            "periodo_final": end_month,
            "quantidade_meses": len(df),
            "receita_total": round(float(receita_total), 2),
            "despesa_apresentada_total": round(
                float(despesa_apresentada), 2
            ),
            "despesa_paga_total": round(
                float(despesa_paga), 2
            ),
            "relacao_apresentada_receita_pct": (
                round(float(despesa_apresentada / receita_total * 100), 2)
                if receita_total > 0
                else None
            ),
            "relacao_paga_receita_pct": (
                round(float(despesa_paga / receita_total * 100), 2)
                if receita_total > 0
                else None
            ),
        }
