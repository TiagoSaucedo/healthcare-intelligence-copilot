from langchain.tools import tool

from app.analytics.services.financial_service import (
    FinancialAnalyticsService,
)
from app.analytics.services.provider_service import (
    ProviderAnalyticsService,
)
from app.analytics.services.procedure_service import (
    ProcedureAnalyticsService,
)
from app.analytics.services.contract_service import (
    ContractAnalyticsService,
)
from app.analytics.services.ranking_service import (
    RankingAnalyticsService,
)


financial_service = FinancialAnalyticsService()
provider_service = ProviderAnalyticsService()
procedure_service = ProcedureAnalyticsService()
contract_service = ContractAnalyticsService()
ranking_service = RankingAnalyticsService()


@tool
def get_financial_summary(
    start_month: str,
    end_month: str,
) -> dict:
    """
    Consulta indicadores financeiros consolidados de um período.

    Retorna receita, despesas apresentadas, despesas pagas
    e relações percentuais entre despesas e receita.

    Os meses devem utilizar o formato YYYY-MM.
    """
    return financial_service.get_financial_summary(
        start_month=start_month,
        end_month=end_month,
    )


@tool
def get_provider_summary(
    start_month: str,
    end_month: str,
) -> dict:
    """
    Consulta indicadores de despesas por prestador em um período.

    Retorna quantidade de prestadores, itens, contas,
    beneficiários e valores médios e totais.

    Os meses devem utilizar o formato YYYY-MM.
    """
    return provider_service.get_provider_summary(
        start_month=start_month,
        end_month=end_month,
    )


@tool
def get_procedure_summary(
    start_month: str,
    end_month: str,
) -> dict:
    """
    Consulta indicadores de despesas por procedimento em um período.

    Retorna quantidade de procedimentos, itens, contas,
    beneficiários, unidades e valores médios e totais.

    Os meses devem utilizar o formato YYYY-MM.
    """
    return procedure_service.get_procedure_summary(
        start_month=start_month,
        end_month=end_month,
    )


@tool
def get_contract_summary(
    start_month: str,
    end_month: str,
) -> dict:
    """
    Consulta indicadores de despesas por contrato em um período.

    Retorna quantidade de contratos, itens, contas,
    beneficiários, procedimentos e valores médios e totais.

    Os meses devem utilizar o formato YYYY-MM.
    """
    return contract_service.get_contract_summary(
        start_month=start_month,
        end_month=end_month,
    )



@tool
def get_expense_ranking(
    dimension: str,
    start_month: str,
    end_month: str,
    limit: int = 10,
    metric: str = "apresentada",
) -> dict:
    """
    Consulta o ranking de entidades por despesa em determinado período.

    Dimensões aceitas:
    - prestador
    - procedimento
    - contrato

    Métricas aceitas:
    - apresentada
    - paga

    Retorna:
    - Ranking das entidades.
    - Quantidade total de entidades na dimensão.
    - Quantidade de entidades retornadas.
    - Valor total da dimensão.
    - Valor acumulado do Top N.
    - Participação percentual conjunta do Top N.

    Os valores e percentuais consolidados são calculados
    deterministicamente pela camada analítica, não pelo LLM.

    Os meses devem utilizar o formato YYYY-MM.
    """

    return ranking_service.get_ranking_analysis(
        dimension=dimension,
        start_month=start_month,
        end_month=end_month,
        limit=limit,
        metric=metric,
    )


@tool
def get_ranking_summary(
    dimension: str,
    start_month: str,
    end_month: str,
    metric: str = "apresentada",
) -> dict:
    """
    Consulta os indicadores consolidados de uma dimensão
    utilizada nos rankings.

    Dimensões aceitas:
    - prestador
    - procedimento
    - contrato

    Métricas aceitas:
    - apresentada
    - paga

    Retorna quantidade de entidades, itens, contas e valor total
    da despesa no período.

    Os meses devem utilizar o formato YYYY-MM.
    """
    return ranking_service.get_ranking_summary(
        dimension=dimension,
        start_month=start_month,
        end_month=end_month,
        metric=metric,
    )


ANALYTICAL_TOOLS = [
    get_financial_summary,
    get_provider_summary,
    get_procedure_summary,
    get_contract_summary,
    get_expense_ranking,
    get_ranking_summary,
]