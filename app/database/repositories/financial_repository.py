import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database.connection import engine


class FinancialRepository:
    """
    Repositório responsável pelas consultas financeiras
    do Healthcare Intelligence Copilot.
    """

    BASE_QUERY = """
        SELECT
            ano_mes,
            receita_competencia,
            despesa_apresentada_atendimento,
            despesa_paga_pagamento,
            relacao_apresentada_receita_pct,
            relacao_paga_receita_pct
        FROM vw_visao_financeira_mensal
    """

    def get_monthly_overview(self) -> pd.DataFrame:
        """Retorna o histórico financeiro mensal completo."""

        query = text(
            self.BASE_QUERY + """
            ORDER BY ano_mes
            """
        )

        try:
            with engine.connect() as connection:
                return pd.read_sql(query, connection)

        except SQLAlchemyError as exc:
            raise RuntimeError(
                "Erro ao consultar a visão financeira mensal."
            ) from exc

    def get_monthly_overview_by_period(
        self,
        start_month: str,
        end_month: str,
    ) -> pd.DataFrame:
        """Retorna os indicadores financeiros de um período."""

        if start_month > end_month:
            raise ValueError(
                "O mês inicial não pode ser posterior ao mês final."
            )

        query = text(
            self.BASE_QUERY + """
            WHERE ano_mes >= :start_month
              AND ano_mes <= :end_month
            ORDER BY ano_mes
            """
        )

        try:
            with engine.connect() as connection:
                return pd.read_sql(
                    query,
                    connection,
                    params={
                        "start_month": start_month,
                        "end_month": end_month,
                    },
                )

        except SQLAlchemyError as exc:
            raise RuntimeError(
                "Erro ao consultar os indicadores financeiros por período."
            ) from exc