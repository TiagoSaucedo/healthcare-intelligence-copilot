
import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database.connection import engine


class ProviderRepository:
    """
    Repositório responsável pelas consultas analíticas
    relacionadas aos prestadores de serviços de saúde.
    """

    BASE_QUERY = """
        SELECT
            ano_mes,
            id_prestador,
            codigo_prestador,
            nome_prestador,
            tipo_prestador,
            especialidade,
            cidade,
            estado,
            total_itens,
            total_contas,
            total_beneficiarios,
            despesa_apresentada,
            despesa_paga,
            valor_medio_por_item,
            valor_medio_por_conta
        FROM vw_despesa_por_prestador
    """

    def get_provider_overview(self) -> pd.DataFrame:
        """Retorna os indicadores por prestador e mês."""

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
                "Erro ao consultar as despesas por prestador."
            ) from exc

    def get_provider_by_period(
        self,
        start_month: str,
        end_month: str,
    ) -> pd.DataFrame:
        """Retorna os indicadores por prestador em um período."""

        if start_month > end_month:
            raise ValueError(
                "O mês inicial não pode ser posterior ao mês final."
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
                "Erro ao consultar despesas por prestador no período."
            ) from exc
