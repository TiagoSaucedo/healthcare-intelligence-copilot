
import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database.connection import engine


class RankingRepository:
    """
    Repositório responsável pelas consultas de rankings
    de despesas assistenciais do Healthcare Intelligence Copilot.
    """

    RANKING_CONFIG = {
        "prestador": {
            "view": "vw_ranking_despesa_prestador",
            "id_column": "id_prestador",
            "name_column": "nome_prestador",
        },
        "procedimento": {
            "view": "vw_ranking_despesa_procedimento",
            "id_column": "id_procedimento",
            "name_column": "descricao",
        },
        "contrato": {
            "view": "vw_ranking_despesa_contrato",
            "id_column": "id_contrato",
            "name_column": "codigo_contrato",
        },
    }

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

        Dimensões:
        - prestador
        - procedimento
        - contrato

        Métricas:
        - apresentada
        - paga
        """

        if dimension not in self.RANKING_CONFIG:
            raise ValueError(
                "Dimensão inválida. Utilize prestador, "
                "procedimento ou contrato."
            )

        if metric not in {"apresentada", "paga"}:
            raise ValueError(
                "Métrica inválida. Utilize apresentada ou paga."
            )

        if start_month > end_month:
            raise ValueError(
                "O mês inicial não pode ser posterior ao mês final."
            )

        if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
            raise ValueError(
                "O limite deve ser um número inteiro positivo."
            )

        config = self.RANKING_CONFIG[dimension]

        value_column = (
            "despesa_apresentada"
            if metric == "apresentada"
            else "despesa_paga"
        )

        query = text(f"""
            WITH despesas AS (
                SELECT
                    {config["id_column"]} AS id_entidade,
                    {config["name_column"]} AS nome_entidade,
                    SUM(quantidade_itens) AS quantidade_itens,
                    SUM(quantidade_contas) AS quantidade_contas,
                    SUM({value_column}) AS valor_despesa
                FROM {config["view"]}
                WHERE ano_mes >= :start_month
                  AND ano_mes <= :end_month
                GROUP BY
                    {config["id_column"]},
                    {config["name_column"]}
            ),
            total AS (
                SELECT SUM(valor_despesa) AS valor_total
                FROM despesas
            )
            SELECT
                DENSE_RANK() OVER (
                    ORDER BY d.valor_despesa DESC
                ) AS ranking,
                d.id_entidade,
                d.nome_entidade,
                d.quantidade_itens,
                d.quantidade_contas,
                d.valor_despesa,
                ROUND(
                    100.0 * d.valor_despesa
                    / NULLIF(t.valor_total, 0),
                    2
                ) AS participacao_pct
            FROM despesas d
            CROSS JOIN total t
            ORDER BY d.valor_despesa DESC
            LIMIT :limit
        """)

        try:
            with engine.connect() as connection:
                return pd.read_sql(
                    query,
                    connection,
                    params={
                        "start_month": start_month,
                        "end_month": end_month,
                        "limit": limit,
                    },
                )

        except SQLAlchemyError as exc:
            raise RuntimeError(
                f"Erro ao consultar o ranking de {dimension}."
            ) from exc

    def get_ranking_totals(
        self,
        dimension: str,
        start_month: str,
        end_month: str,
        metric: str = "apresentada",
    ) -> dict:
        """
        Retorna os totais consolidados da dimensão no período.

        Permite validar a reconciliação financeira do ranking,
        independentemente do limite de registros apresentado.
        """

        if dimension not in self.RANKING_CONFIG:
            raise ValueError("Dimensão inválida.")

        if metric not in {"apresentada", "paga"}:
            raise ValueError(
                "Métrica inválida. Utilize apresentada ou paga."
            )

        if start_month > end_month:
            raise ValueError(
                "O mês inicial não pode ser posterior ao mês final."
            )

        config = self.RANKING_CONFIG[dimension]

        value_column = (
            "despesa_apresentada"
            if metric == "apresentada"
            else "despesa_paga"
        )

        query = text(f"""
            SELECT
                COUNT(DISTINCT {config["id_column"]})
                    AS quantidade_entidades,
                SUM({value_column}) AS valor_total,
                SUM(quantidade_itens) AS quantidade_itens,
                SUM(quantidade_contas) AS quantidade_contas
            FROM {config["view"]}
            WHERE ano_mes >= :start_month
              AND ano_mes <= :end_month
        """)

        try:
            with engine.connect() as connection:
                result = pd.read_sql(
                    query,
                    connection,
                    params={
                        "start_month": start_month,
                        "end_month": end_month,
                    },
                )

                return result.iloc[0].to_dict()

        except SQLAlchemyError as exc:
            raise RuntimeError(
                f"Erro ao consultar os totais do ranking de {dimension}."
            ) from exc
