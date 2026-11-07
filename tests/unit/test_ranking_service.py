
import pandas as pd
import pytest

from app.analytics.services.ranking_service import (
    RankingAnalyticsService,
)


class FakeRankingRepository:
    def get_ranking(
        self,
        dimension,
        start_month,
        end_month,
        limit,
        metric,
    ):
        return pd.DataFrame(
            [
                {
                    "ranking": 1,
                    "id_entidade": 10,
                    "nome_entidade": "Entidade A",
                    "quantidade_itens": 100,
                    "quantidade_contas": 80,
                    "valor_despesa": 50000.0,
                    "participacao_pct": 15.0,
                }
            ]
        )

    def get_ranking_totals(
        self,
        dimension,
        start_month,
        end_month,
        metric,
    ):
        return pd.Series(
            {
                "quantidade_entidades": 150,
                "quantidade_itens": 1000,
                "quantidade_contas": 800,
                "valor_total": 333000.0,
            }
        )


@pytest.fixture
def service():
    return RankingAnalyticsService(
        repository=FakeRankingRepository()
    )


def test_get_ranking_returns_dataframe(service):
    result = service.get_ranking(
        dimension="prestador",
        start_month="2028-01",
        end_month="2028-12",
    )

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1
    assert result.iloc[0]["nome_entidade"] == "Entidade A"


def test_get_ranking_summary_returns_expected_data(service):
    result = service.get_ranking_summary(
        dimension="prestador",
        start_month="2028-01",
        end_month="2028-12",
    )

    assert result["dimensao"] == "prestador"
    assert result["metrica"] == "apresentada"
    assert result["periodo_inicial"] == "2028-01"
    assert result["periodo_final"] == "2028-12"
    assert result["quantidade_entidades"] == 150
    assert result["quantidade_itens"] == 1000
    assert result["quantidade_contas"] == 800
    assert result["valor_total"] == 333000.0


@pytest.mark.parametrize(
    "dimension",
    ["invalida", "", None],
)
def test_invalid_dimension_raises_error(service, dimension):
    with pytest.raises(ValueError):
        service.get_ranking(
            dimension=dimension,
            start_month="2028-01",
            end_month="2028-12",
        )


@pytest.mark.parametrize(
    "metric",
    ["invalida", "", None],
)
def test_invalid_metric_raises_error(service, metric):
    with pytest.raises(ValueError):
        service.get_ranking(
            dimension="prestador",
            start_month="2028-01",
            end_month="2028-12",
            metric=metric,
        )


@pytest.mark.parametrize(
    "start_month,end_month",
    [
        ("2028-13", "2028-12"),
        ("2028-00", "2028-12"),
        ("28-01", "2028-12"),
        ("2028-01", "2028-13"),
        ("2028-12", "2028-01"),
    ],
)
def test_invalid_period_raises_error(
    service,
    start_month,
    end_month,
):
    with pytest.raises(ValueError):
        service.get_ranking(
            dimension="prestador",
            start_month=start_month,
            end_month=end_month,
        )


@pytest.mark.parametrize(
    "limit",
    [0, -1, 1.5, True],
)
def test_invalid_limit_raises_error(service, limit):
    with pytest.raises(ValueError):
        service.get_ranking(
            dimension="prestador",
            start_month="2028-01",
            end_month="2028-12",
            limit=limit,
        )


def test_get_ranking_passes_parameters_to_repository():
    class SpyRepository(FakeRankingRepository):
        def get_ranking(
            self,
            dimension,
            start_month,
            end_month,
            limit,
            metric,
        ):
            self.received = {
                "dimension": dimension,
                "start_month": start_month,
                "end_month": end_month,
                "limit": limit,
                "metric": metric,
            }
            return pd.DataFrame()

    repository = SpyRepository()
    service = RankingAnalyticsService(repository=repository)

    service.get_ranking(
        dimension="procedimento",
        start_month="2028-01",
        end_month="2028-06",
        limit=20,
        metric="paga",
    )

    assert repository.received == {
        "dimension": "procedimento",
        "start_month": "2028-01",
        "end_month": "2028-06",
        "limit": 20,
        "metric": "paga",
    }


def test_get_ranking_summary_handles_null_totals():
    class NullRepository(FakeRankingRepository):
        def get_ranking_totals(
            self,
            dimension,
            start_month,
            end_month,
            metric,
        ):
            return pd.Series(
                {
                    "quantidade_entidades": 0,
                    "quantidade_itens": None,
                    "quantidade_contas": None,
                    "valor_total": None,
                }
            )

    service = RankingAnalyticsService(
        repository=NullRepository()
    )

    result = service.get_ranking_summary(
        dimension="prestador",
        start_month="2028-01",
        end_month="2028-12",
    )

    assert result["quantidade_itens"] == 0
    assert result["quantidade_contas"] == 0
    assert result["valor_total"] == 0.0


def test_get_ranking_analysis_calculates_combined_participation():
    service = RankingAnalyticsService(
        repository=FakeRankingRepository()
    )

    result = service.get_ranking_analysis(
        dimension="prestador",
        start_month="2028-01",
        end_month="2028-12",
        limit=5,
        metric="apresentada",
    )

    assert result["dimensao"] == "prestador"
    assert result["metrica"] == "apresentada"
    assert result["quantidade_entidades_total"] == 150
    assert result["quantidade_entidades_retornadas"] == 1
    assert result["valor_total_dimensao"] == 333000.0
    assert result["valor_total_top_n"] == 50000.0

    # 50.000 / 333.000 * 100 = 15,015...%
    assert result["participacao_conjunta_pct"] == 15.02

    assert len(result["resultados"]) == 1


def test_get_ranking_analysis_handles_empty_ranking():
    class EmptyRankingRepository(FakeRankingRepository):
        def get_ranking(
            self,
            dimension,
            start_month,
            end_month,
            limit,
            metric,
        ):
            return pd.DataFrame(
                columns=[
                    "ranking",
                    "id_entidade",
                    "nome_entidade",
                    "quantidade_itens",
                    "quantidade_contas",
                    "valor_despesa",
                    "participacao_pct",
                ]
            )

    service = RankingAnalyticsService(
        repository=EmptyRankingRepository()
    )

    result = service.get_ranking_analysis(
        dimension="prestador",
        start_month="2028-01",
        end_month="2028-12",
    )

    assert result["quantidade_entidades_retornadas"] == 0
    assert result["valor_total_top_n"] == 0.0
    assert result["participacao_conjunta_pct"] == 0.0
    assert result["resultados"] == []


def test_get_ranking_analysis_handles_zero_dimension_total():
    class ZeroTotalRepository(FakeRankingRepository):
        def get_ranking_totals(
            self,
            dimension,
            start_month,
            end_month,
            metric,
        ):
            return pd.Series(
                {
                    "quantidade_entidades": 0,
                    "quantidade_itens": 0,
                    "quantidade_contas": 0,
                    "valor_total": 0,
                }
            )

    service = RankingAnalyticsService(
        repository=ZeroTotalRepository()
    )

    result = service.get_ranking_analysis(
        dimension="prestador",
        start_month="2028-01",
        end_month="2028-12",
    )

    assert result["valor_total_dimensao"] == 0.0
    assert result["participacao_conjunta_pct"] == 0.0
