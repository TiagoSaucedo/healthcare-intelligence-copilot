
import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database.connection import engine


class ContractRepository:
    """
    Repositório responsável pelas consultas analíticas
    relacionadas aos contratos de assistência à saúde.
    """

    BASE_QUERY = """
        SELECT
            ano_mes,
            id_contrato,
            codigo_contrato,
            modalidade,
            cobertura,
            acomodacao,
            tipo_contrato,
            quantidade_itens,
            quantidade_contas,
            quantidade_beneficiarios,
            quantidade_procedimentos,
            valor_total_apresentado,
            valor_total_pago,
            media_valor_por_item,
            media_valor_por_conta
        FROM vw_despesa_por_contrato
    """

    def get_contract_overview(self) -> pd.DataFrame:
        """Retorna os indicadores por contrato e mês."""

        query = text(
            self.BASE_QUERY + """
            ORDER BY ano_mes, valor_total_apresentado DESC
            """
        )

        try:
            with engine.connect() as connection:
                return pd.read_sql(query, connection)

        except SQLAlchemyError as exc:
            raise RuntimeError(
                "Erro ao consultar as despesas por contrato."
            ) from exc

    def get_contract_by_period(
        self,
        start_month: str,
        end_month: str,
    ) -> pd.DataFrame:
        """Retorna os indicadores por contrato em um período."""

        if start_month > end_month:
            raise ValueError(
                "O mês inicial não pode ser posterior ao final."
            )

        query = text(
            self.BASE_QUERY + """
            WHERE ano_mes >= :start_month
              AND ano_mes <= :end_month
            ORDER BY ano_mes, valor_total_apresentado DESC
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
                "Erro ao consultar despesas por contrato no período."
            ) from exc
