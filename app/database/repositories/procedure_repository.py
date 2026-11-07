
import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database.connection import engine


class ProcedureRepository:
    """
    Repositório responsável pelas consultas analíticas
    relacionadas aos procedimentos assistenciais.
    """

    BASE_QUERY = """
        SELECT
            ano_mes,
            id_procedimento,
            codigo_procedimento,
            descricao,
            grupo_procedimento,
            categoria,
            tipo_procedimento,
            total_itens,
            total_contas,
            total_beneficiarios,
            quantidade_total,
            despesa_apresentada,
            despesa_paga,
            valor_medio_por_item,
            valor_medio_por_unidade
        FROM vw_despesa_por_procedimento
    """

    def get_procedure_overview(self) -> pd.DataFrame:
        """Retorna os indicadores por procedimento e mês."""

        query = text(
            self.BASE_QUERY + """
            ORDER BY ano_mes, despesa_apresentada DESC
            """
        )

        try:
            with engine.connect() as connection:
                return pd.read_sql(query, connection)

        except SQLAlchemyError as exc:
            raise RuntimeError(
                "Erro ao consultar as despesas por procedimento."
            ) from exc

    def get_procedure_by_period(
        self,
        start_month: str,
        end_month: str,
    ) -> pd.DataFrame:
        """Retorna os indicadores por procedimento em um período."""

        if start_month > end_month:
            raise ValueError(
                "O mês inicial não pode ser posterior ao final."
            )

        query = text(
            self.BASE_QUERY + """
            WHERE ano_mes >= :start_month
              AND ano_mes <= :end_month
            ORDER BY ano_mes, despesa_apresentada DESC
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
                "Erro ao consultar despesas por procedimento no período."
            ) from exc
