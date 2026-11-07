
import pytest

from app.database.repositories.ranking_repository import (
    RankingRepository,
)


@pytest.fixture
def repository():
    return RankingRepository()


@pytest.mark.parametrize(
    "dimension, expected_entities",
    [
        ("prestador", 150),
        ("procedimento", 200),
        ("contrato", 50),
    ],
)
def test_ranking_returns_expected_entities(
    repository,
    dimension,
    expected_entities,
):
    result = repository.get_ranking(
        dimension=dimension,
        start_month="2028-01",
        end_month="2028-12",
        limit=10,
    )

    assert not result.empty
    assert len(result) == 10
    assert result["ranking"].is_monotonic_increasing
    assert result["valor_despesa"].is_monotonic_decreasing
    assert result["participacao_pct"].ge(0).all()


@pytest.mark.parametrize(
    "dimension",
    ["prestador", "procedimento", "contrato"],
)
def test_ranking_totals_reconcile_with_financial_data(
    repository,
    dimension,
):
    result = repository.get_ranking_totals(
        dimension=dimension,
        start_month="2028-01",
        end_month="2028-12",
    )

    assert result["quantidade_entidades"] in {50, 150, 200}
    assert result["valor_total"] == pytest.approx(
        3326864.19,
        abs=0.01,
    )


def test_top_ten_does_not_represent_total_expense(
    repository,
):
    ranking = repository.get_ranking(
        dimension="prestador",
        start_month="2028-01",
        end_month="2028-12",
        limit=10,
    )

    totals = repository.get_ranking_totals(
        dimension="prestador",
        start_month="2028-01",
        end_month="2028-12",
    )

    top_ten_total = ranking["valor_despesa"].sum()

    assert top_ten_total < totals["valor_total"]


def test_ranking_participation_uses_full_period_total(
    repository,
):
    ranking = repository.get_ranking(
        dimension="prestador",
        start_month="2028-01",
        end_month="2028-12",
        limit=10,
    )

    totals = repository.get_ranking_totals(
        dimension="prestador",
        start_month="2028-01",
        end_month="2028-12",
    )

    expected_participation = (
        ranking.iloc[0]["valor_despesa"]
        / totals["valor_total"]
    ) * 100

    assert ranking.iloc[0]["participacao_pct"] == pytest.approx(
        expected_participation,
        abs=0.01,
    )


@pytest.mark.parametrize(
    "dimension",
    ["invalido", "", None],
)
def test_invalid_dimension_raises_error(
    repository,
    dimension,
):
    with pytest.raises(ValueError):
        repository.get_ranking(
            dimension=dimension,
            start_month="2028-01",
            end_month="2028-12",
        )


@pytest.mark.parametrize(
    "metric",
    ["invalida", "", None],
)
def test_invalid_metric_raises_error(
    repository,
    metric,
):
    with pytest.raises(ValueError):
        repository.get_ranking(
            dimension="prestador",
            start_month="2028-01",
            end_month="2028-12",
            metric=metric,
        )


def test_invalid_period_raises_error(repository):
    with pytest.raises(ValueError):
        repository.get_ranking(
            dimension="prestador",
            start_month="2028-12",
            end_month="2028-01",
        )


@pytest.mark.parametrize(
    "limit",
    [0, -1, 1.5, True],
)
def test_invalid_limit_raises_error(repository, limit):
    with pytest.raises(ValueError):
        repository.get_ranking(
            dimension="prestador",
            start_month="2028-01",
            end_month="2028-12",
            limit=limit,
        )
