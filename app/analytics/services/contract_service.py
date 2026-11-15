
import re
from typing import ClassVar

import pandas as pd

from app.analytics.services.common import (
    normalize_numeric_columns,
    safe_divide,
    safe_sum,
    validate_required_columns,
)
from app.database.repositories.contract_repository import (
    ContractRepository,
)


class ContractAnalyticsService:
    """
    Camada de serviços responsável pelas análises de contratos.

    Centraliza regras de negócio e prepara os dados para
    consumo dos agentes analíticos.
    """

    REQUIRED_COLUMNS: ClassVar[list[str]] = [
        "id_contrato",
        "quantidade_itens",
        "quantidade_contas",
        "quantidade_beneficiarios",
        "quantidade_procedimentos",
        "valor_total_apresentado",
        "valor_total_pago",
    ]

    NUMERIC_COLUMNS: ClassVar[list[str]] = [
        "quantidade_itens",
        "quantidade_contas",
        "quantidade_beneficiarios",
        "quantidade_procedimentos",
        "valor_total_apresentado",
        "valor_total_pago",
    ]

    def __init__(
        self,
        repository: ContractRepository | None = None,
    ):
        self.repository = repository or ContractRepository()

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

    def get_contract_overview(self) -> pd.DataFrame:
        """Retorna o histórico completo de despesas por contrato."""

        return self.repository.get_contract_overview()

    def get_contract_by_period(
        self,
        start_month: str,
        end_month: str,
    ) -> pd.DataFrame:
        """Retorna as despesas por contrato em determinado período."""

        self._validate_period(start_month, end_month)

        return self.repository.get_contract_by_period(
            start_month=start_month,
            end_month=end_month,
        )

    def get_contract_summary(
        self,
        start_month: str,
        end_month: str,
    ) -> dict:
        """
        Consolida os principais indicadores de despesas
        por contrato no período informado.
        """

        df = self.get_contract_by_period(
            start_month=start_month,
            end_month=end_month,
        )

        if df.empty:
            return {
                "periodo_inicial": start_month,
                "periodo_final": end_month,
                "quantidade_contratos": 0,
                "quantidade_itens": 0,
                "quantidade_contas": 0,
                "quantidade_beneficiarios": 0,
                "quantidade_procedimentos": 0,
                "despesa_apresentada_total": 0.0,
                "despesa_paga_total": 0.0,
                "valor_medio_por_item": None,
                "valor_medio_por_conta": None,
            }

        validate_required_columns(df, self.REQUIRED_COLUMNS)

        df = normalize_numeric_columns(
            df,
            self.NUMERIC_COLUMNS,
        )

        despesa_apresentada = safe_sum(
            df["valor_total_apresentado"]
        )
        despesa_paga = safe_sum(df["valor_total_pago"])
        total_itens = safe_sum(df["quantidade_itens"])
        total_contas = safe_sum(df["quantidade_contas"])
        total_beneficiarios = safe_sum(
            df["quantidade_beneficiarios"]
        )
        total_procedimentos = safe_sum(
            df["quantidade_procedimentos"]
        )

        media_por_item = safe_divide(
            despesa_apresentada,
            total_itens,
        )
        media_por_conta = safe_divide(
            despesa_apresentada,
            total_contas,
        )

        return {
            "periodo_inicial": start_month,
            "periodo_final": end_month,
            "quantidade_contratos": int(
                df["id_contrato"].nunique()
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
            "quantidade_procedimentos": (
                int(total_procedimentos)
                if total_procedimentos is not None
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
            "valor_medio_por_conta": (
                round(media_por_conta, 2)
                if media_por_conta is not None
                else None
            ),
        }
