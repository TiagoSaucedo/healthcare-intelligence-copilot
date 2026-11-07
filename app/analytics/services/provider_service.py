import re

import pandas as pd

from app.database.repositories.provider_repository import (
    ProviderRepository,
)


class ProviderAnalyticsService:
    """
    Camada de serviços responsável pelas análises de prestadores.

    Centraliza regras de negócio e prepara os dados para
    consumo dos agentes analíticos.
    """

    def __init__(
        self,
        repository: ProviderRepository | None = None,
    ):
        self.repository = repository or ProviderRepository()

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

    def get_provider_overview(self) -> pd.DataFrame:
        """Retorna o histórico completo de despesas por prestador."""

        return self.repository.get_provider_overview()

    def get_provider_by_period(
        self,
        start_month: str,
        end_month: str,
    ) -> pd.DataFrame:
        """Retorna as despesas por prestador em determinado período."""

        self._validate_period(start_month, end_month)

        return self.repository.get_provider_by_period(
            start_month=start_month,
            end_month=end_month,
        )

    def get_provider_summary(
        self,
        start_month: str,
        end_month: str,
    ) -> dict:
        """
        Consolida os principais indicadores de despesas
        por prestador no período informado.
        """

        df = self.get_provider_by_period(
            start_month=start_month,
            end_month=end_month,
        )

        if df.empty:
            return {
                "periodo_inicial": start_month,
                "periodo_final": end_month,
                "quantidade_prestadores": 0,
                "quantidade_itens": 0,
                "quantidade_contas": 0,
                "quantidade_beneficiarios": 0,
                "despesa_apresentada_total": 0.0,
                "despesa_paga_total": 0.0,
                "valor_medio_por_item": None,
                "valor_medio_por_conta": None,
            }

        despesa_apresentada = df["despesa_apresentada"].sum()
        despesa_paga = df["despesa_paga"].sum()

        total_itens = df["total_itens"].sum()
        total_contas = df["total_contas"].sum()

        return {
            "periodo_inicial": start_month,
            "periodo_final": end_month,
            "quantidade_prestadores": int(
                df["id_prestador"].nunique()
            ),
            "quantidade_itens": int(total_itens),
            "quantidade_contas": int(total_contas),
            "quantidade_beneficiarios": int(
                df["total_beneficiarios"].sum()
            ),
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
            "valor_medio_por_conta": (
                round(
                    float(despesa_apresentada / total_contas), 2
                )
                if total_contas > 0
                else None
            ),
        }