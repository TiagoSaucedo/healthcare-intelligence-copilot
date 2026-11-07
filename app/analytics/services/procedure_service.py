import re

import pandas as pd

from app.database.repositories.procedure_repository import (
    ProcedureRepository,
)


class ProcedureAnalyticsService:
    """
    Camada de serviços responsável pelas análises de procedimentos.

    Centraliza regras de negócio e prepara os dados para
    consumo dos agentes analíticos.
    """

    def __init__(
        self,
        repository: ProcedureRepository | None = None,
    ):
        self.repository = repository or ProcedureRepository()

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

    def get_procedure_overview(self) -> pd.DataFrame:
        """Retorna o histórico completo de despesas por procedimento."""

        return self.repository.get_procedure_overview()

    def get_procedure_by_period(
        self,
        start_month: str,
        end_month: str,
    ) -> pd.DataFrame:
        """Retorna as despesas por procedimento em determinado período."""

        self._validate_period(start_month, end_month)

        return self.repository.get_procedure_by_period(
            start_month=start_month,
            end_month=end_month,
        )

    def get_procedure_summary(
        self,
        start_month: str,
        end_month: str,
    ) -> dict:
        """
        Consolida os principais indicadores de despesas
        por procedimento no período informado.
        """

        df = self.get_procedure_by_period(
            start_month=start_month,
            end_month=end_month,
        )

        if df.empty:
            return {
                "periodo_inicial": start_month,
                "periodo_final": end_month,
                "quantidade_procedimentos": 0,
                "quantidade_itens": 0,
                "quantidade_contas": 0,
                "quantidade_beneficiarios": 0,
                "quantidade_total": 0.0,
                "despesa_apresentada_total": 0.0,
                "despesa_paga_total": 0.0,
                "valor_medio_por_item": None,
                "valor_medio_por_unidade": None,
            }

        despesa_apresentada = df["despesa_apresentada"].sum()
        despesa_paga = df["despesa_paga"].sum()

        total_itens = df["total_itens"].sum()
        quantidade_total = df["quantidade_total"].sum()

        return {
            "periodo_inicial": start_month,
            "periodo_final": end_month,
            "quantidade_procedimentos": int(
                df["id_procedimento"].nunique()
            ),
            "quantidade_itens": int(total_itens),
            "quantidade_contas": int(df["total_contas"].sum()),
            "quantidade_beneficiarios": int(
                df["total_beneficiarios"].sum()
            ),
            "quantidade_total": float(quantidade_total),
            "despesa_apresentada_total": round(
                float(despesa_apresentada), 2
            ),
            "despesa_paga_total": round(
                float(despesa_paga), 2
            ),
            "valor_medio_por_item": (
                round(
                    float(despesa_apresentada / total_itens), 2
                )
                if total_itens > 0
                else None
            ),
            "valor_medio_por_unidade": (
                round(
                    float(despesa_apresentada / quantidade_total), 2
                )
                if quantidade_total > 0
                else None
            ),
        }