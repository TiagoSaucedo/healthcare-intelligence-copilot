import re
from typing import ClassVar

import pandas as pd

from app.analytics.services.common import (
    normalize_numeric_columns,
    safe_divide,
    safe_sum,
    validate_required_columns,
)
from app.database.repositories.provider_repository import (
    ProviderRepository,
)


class ProviderAnalyticsService:
    REQUIRED_COLUMNS: ClassVar[list[str]] = [
        "id_prestador",
        "despesa_apresentada",
        "despesa_paga",
        "total_itens",
        "total_contas",
        "total_beneficiarios",
    ]

    NUMERIC_COLUMNS: ClassVar[list[str]] = [
        "despesa_apresentada",
        "despesa_paga",
        "total_itens",
        "total_contas",
        "total_beneficiarios",
    ]

    PAID_REQUIRED_COLUMNS: ClassVar[list[str]] = [
        "id_prestador",
        "despesa_paga",
        "total_itens_pagos",
        "total_contas_pagas",
        "total_beneficiarios",
    ]

    PAID_NUMERIC_COLUMNS: ClassVar[list[str]] = [
        "despesa_paga",
        "total_itens_pagos",
        "total_contas_pagas",
        "total_beneficiarios",
    ]

    def __init__(
        self,
        repository: ProviderRepository | None = None,
    ):
        self.repository = repository or ProviderRepository()

    @staticmethod
    def _validate_period(start_month: str, end_month: str) -> None:
        pattern = r"^\d{4}-(0[1-9]|1[0-2])$"

        for month in (start_month, end_month):
            if not isinstance(month, str) or not re.fullmatch(pattern, month):
                raise ValueError(
                    "O perÃ­odo deve utilizar o formato YYYY-MM."
                )

        if start_month > end_month:
            raise ValueError(
                "O mÃªs inicial nÃ£o pode ser posterior ao final."
            )

    def get_provider_overview(self) -> pd.DataFrame:
        return self.repository.get_provider_overview()

    def get_provider_by_period(
        self,
        start_month: str,
        end_month: str,
    ) -> pd.DataFrame:
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
        df = self.get_provider_by_period(start_month, end_month)

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

        validate_required_columns(df, self.REQUIRED_COLUMNS)
        df = normalize_numeric_columns(df, self.NUMERIC_COLUMNS)

        despesa_apresentada = safe_sum(df["despesa_apresentada"])
        despesa_paga = safe_sum(df["despesa_paga"])
        total_itens = safe_sum(df["total_itens"])
        total_contas = safe_sum(df["total_contas"])
        total_beneficiarios = safe_sum(df["total_beneficiarios"])

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
            "quantidade_prestadores": int(df["id_prestador"].nunique()),
            "quantidade_itens": (
                int(total_itens) if total_itens is not None else None
            ),
            "quantidade_contas": (
                int(total_contas) if total_contas is not None else None
            ),
            "quantidade_beneficiarios": (
                int(total_beneficiarios)
                if total_beneficiarios is not None
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

    def get_paid_provider_overview(self) -> pd.DataFrame:
        """Retorna os pagamentos por prestador e mÃªs de pagamento."""

        return self.repository.get_paid_provider_overview()

    def get_paid_provider_by_period(
        self,
        start_month: str,
        end_month: str,
    ) -> pd.DataFrame:
        """Retorna os pagamentos por prestador no perÃ­odo."""

        self._validate_period(start_month, end_month)

        return self.repository.get_paid_provider_by_period(
            start_month=start_month,
            end_month=end_month,
        )

    def get_paid_provider_summary(
        self,
        start_month: str,
        end_month: str,
    ) -> dict:
        """Consolida indicadores financeiros por mÃªs de pagamento."""

        df = self.get_paid_provider_by_period(
            start_month,
            end_month,
        )

        if df.empty:
            return {
                "periodo_inicial": start_month,
                "periodo_final": end_month,
                "quantidade_prestadores": 0,
                "quantidade_itens_pagos": 0,
                "quantidade_contas_pagas_mes_acumulada": 0,
                "quantidade_beneficiarios_mes_acumulada": 0,
                "despesa_paga_total": 0.0,
                "valor_medio_pago_por_item": None,
                "valor_medio_pago_por_conta": None,
            }

        validate_required_columns(df, self.PAID_REQUIRED_COLUMNS)

        df = normalize_numeric_columns(
            df,
            self.PAID_NUMERIC_COLUMNS,
        )

        despesa_paga = safe_sum(df["despesa_paga"])
        total_itens = safe_sum(df["total_itens_pagos"])
        total_contas = safe_sum(df["total_contas_pagas"])
        total_beneficiarios = safe_sum(df["total_beneficiarios"])

        media_por_item = safe_divide(
            despesa_paga,
            total_itens,
        )
        media_por_conta = safe_divide(
            despesa_paga,
            total_contas,
        )

        return {
            "periodo_inicial": start_month,
            "periodo_final": end_month,
            "quantidade_prestadores": int(df["id_prestador"].nunique()),
            "quantidade_itens_pagos": (
                int(total_itens) if total_itens is not None else None
            ),
            "quantidade_contas_pagas_mes_acumulada": (
                int(total_contas) if total_contas is not None else None
            ),
            "quantidade_beneficiarios_mes_acumulada": (
                int(total_beneficiarios)
                if total_beneficiarios is not None
                else None
            ),
            "despesa_paga_total": (
                round(despesa_paga, 2)
                if despesa_paga is not None
                else None
            ),
            "valor_medio_pago_por_item": (
                round(media_por_item, 2)
                if media_por_item is not None
                else None
            ),
            "valor_medio_pago_por_conta": (
                round(media_por_conta, 2)
                if media_por_conta is not None
                else None
            ),
        }
