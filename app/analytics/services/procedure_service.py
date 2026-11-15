
import re
from typing import ClassVar

import pandas as pd

from app.analytics.services.common import (
    normalize_numeric_columns,
    safe_divide,
    safe_sum,
    validate_required_columns,
)
from app.database.repositories.procedure_repository import (
    ProcedureRepository,
)


class ProcedureAnalyticsService:
    """
    Camada de serviços responsável pelas análises de procedimentos.

    Centraliza regras de negócio e prepara os dados para
    consumo dos agentes analíticos.
    """

    REQUIRED_COLUMNS: ClassVar[list[str]] = [
        "id_procedimento",
        "despesa_apresentada",
        "despesa_paga",
        "total_itens",
        "total_contas",
        "total_beneficiarios",
        "quantidade_total",
    ]

    NUMERIC_COLUMNS: ClassVar[list[str]] = [
        "despesa_apresentada",
        "despesa_paga",
        "total_itens",
        "total_contas",
        "total_beneficiarios",
        "quantidade_total",
    ]

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

        validate_required_columns(df, self.REQUIRED_COLUMNS)

        df = normalize_numeric_columns(
            df,
            self.NUMERIC_COLUMNS,
        )

        despesa_apresentada = safe_sum(
            df["despesa_apresentada"]
        )
        despesa_paga = safe_sum(df["despesa_paga"])
        total_itens = safe_sum(df["total_itens"])
        total_contas = safe_sum(df["total_contas"])
        total_beneficiarios = safe_sum(
            df["total_beneficiarios"]
        )
        quantidade_total = safe_sum(
            df["quantidade_total"]
        )

        media_por_item = safe_divide(
            despesa_apresentada,
            total_itens,
        )
        media_por_unidade = safe_divide(
            despesa_apresentada,
            quantidade_total,
        )

        return {
            "periodo_inicial": start_month,
            "periodo_final": end_month,
            "quantidade_procedimentos": int(
                df["id_procedimento"].nunique()
            ),
            "quantidade_itens": (
                int(total_itens)
                if total_itens is not None
                else None
            ),
            "quantidade_contas": (
                int(total_contas)
                if total_contas is not None
                else None
            ),
            "quantidade_beneficiarios": (
                int(total_beneficiarios)
                if total_beneficiarios is not None
                else None
            ),
            "quantidade_total": (
                float(quantidade_total)
                if quantidade_total is not None
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
            "valor_medio_por_item": (
                round(media_por_item, 2)
                if media_por_item is not None
                else None
            ),
            "valor_medio_por_unidade": (
                round(media_por_unidade, 2)
                if media_por_unidade is not None
                else None
            ),
        }
