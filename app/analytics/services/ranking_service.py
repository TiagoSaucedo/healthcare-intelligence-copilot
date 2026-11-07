
import re
from decimal import Decimal, ROUND_HALF_UP

import pandas as pd

from app.database.repositories.ranking_repository import (
    RankingRepository,
)


class RankingAnalyticsService:
    """
    Serviço responsável pela análise e consolidação
    dos rankings de despesas assistenciais.
    """

    VALID_DIMENSIONS = {
        "prestador",
        "procedimento",
        "contrato",
    }

    VALID_METRICS = {
        "apresentada",
        "paga",
    }

    def __init__(
        self,
        repository: RankingRepository | None = None,
    ):
        self.repository = repository or RankingRepository()

    @staticmethod
    def _validate_period(
        start_month: str,
        end_month: str,
    ) -> None:
        pattern = r"^\d{4}-(0[1-9]|1[0-2])$"

        if not re.match(pattern, start_month):
            raise ValueError(
                "Mês inicial inválido. Utilize YYYY-MM."
            )

        if not re.match(pattern, end_month):
            raise ValueError(
                "Mês final inválido. Utilize YYYY-MM."
            )

        if start_month > end_month:
            raise ValueError(
                "O mês inicial não pode ser posterior ao mês final."
            )

    def get_ranking(
        self,
        dimension: str,
        start_month: str,
        end_month: str,
        limit: int = 10,
        metric: str = "apresentada",
    ) -> pd.DataFrame:
        """
        Retorna o ranking de despesas por dimensão e período.
        """

        self._validate_period(start_month, end_month)

        if dimension not in self.VALID_DIMENSIONS:
            raise ValueError(
                "Dimensão inválida. Utilize prestador, "
                "procedimento ou contrato."
            )

        if metric not in self.VALID_METRICS:
            raise ValueError(
                "Métrica inválida. Utilize apresentada ou paga."
            )

        if (
            not isinstance(limit, int)
            or isinstance(limit, bool)
            or limit < 1
        ):
            raise ValueError(
                "O limite deve ser um número inteiro positivo."
            )

        return self.repository.get_ranking(
            dimension=dimension,
            start_month=start_month,
            end_month=end_month,
            limit=limit,
            metric=metric,
        )

    def get_ranking_summary(
        self,
        dimension: str,
        start_month: str,
        end_month: str,
        metric: str = "apresentada",
    ) -> dict:
        """
        Retorna os totais consolidados de uma dimensão no período.
        """

        self._validate_period(start_month, end_month)

        if dimension not in self.VALID_DIMENSIONS:
            raise ValueError("Dimensão inválida.")

        if metric not in self.VALID_METRICS:
            raise ValueError(
                "Métrica inválida. Utilize apresentada ou paga."
            )

        totals = self.repository.get_ranking_totals(
            dimension=dimension,
            start_month=start_month,
            end_month=end_month,
            metric=metric,
        )

        return {
            "dimensao": dimension,
            "metrica": metric,
            "periodo_inicial": start_month,
            "periodo_final": end_month,
            "quantidade_entidades": int(
                0 if pd.isna(totals["quantidade_entidades"])
                else totals["quantidade_entidades"]
            ),
            "quantidade_itens": int(
                0 if pd.isna(totals["quantidade_itens"])
                else totals["quantidade_itens"]
            ),
            "quantidade_contas": int(
                0 if pd.isna(totals["quantidade_contas"])
                else totals["quantidade_contas"]
            ),
            "valor_total": float(
                0 if pd.isna(totals["valor_total"])
                else totals["valor_total"]
            ),
        }

    def get_ranking_analysis(
        self,
        dimension: str,
        start_month: str,
        end_month: str,
        limit: int = 10,
        metric: str = "apresentada",
    ) -> dict:
        """
        Retorna o ranking acompanhado de indicadores consolidados.

        Os cálculos de participação são realizados nesta camada,
        sem depender do LLM.
        """

        ranking = self.get_ranking(
            dimension=dimension,
            start_month=start_month,
            end_month=end_month,
            limit=limit,
            metric=metric,
        )

        summary = self.get_ranking_summary(
            dimension=dimension,
            start_month=start_month,
            end_month=end_month,
            metric=metric,
        )

        if ranking.empty:
            valor_total_top_n = Decimal("0.00")
        else:
            if ranking.empty:
                valor_total_top_n = Decimal("0.00")
            else:
                valor_total_top_n = sum(
                    (
                        Decimal(str(valor))
                        for valor in ranking["valor_despesa"].dropna()
                    ),
                    Decimal("0.00"),
                )

        valor_total_dimensao = Decimal(
            str(summary["valor_total"])
        )

        if valor_total_dimensao > 0:
            participacao_conjunta = (
                valor_total_top_n
                / valor_total_dimensao
                * Decimal("100")
            ).quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP,
            )
        else:
            participacao_conjunta = Decimal("0.00")

        return {
            "dimensao": dimension,
            "metrica": metric,
            "periodo_inicial": start_month,
            "periodo_final": end_month,
            "quantidade_entidades_total": (
                summary["quantidade_entidades"]
            ),
            "quantidade_entidades_retornadas": len(ranking),
            "valor_total_dimensao": float(
                valor_total_dimensao
            ),
            "valor_total_top_n": float(
                valor_total_top_n.quantize(
                    Decimal("0.01"),
                    rounding=ROUND_HALF_UP,
                )
            ),
            "participacao_conjunta_pct": float(
                participacao_conjunta
            ),
            "resultados": ranking.to_dict(
                orient="records"
            ),
        }
