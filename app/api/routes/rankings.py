import json
import logging

from fastapi import APIRouter, HTTPException, Query

from app.analytics.services.ranking_service import (
    RankingAnalyticsService,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/analytics/rankings",
    tags=["Ranking Analytics"],
)

PERIOD_PATTERN = r"^\d{4}-(0[1-9]|1[0-2])$"


@router.get("")
def get_ranking(
    dimension: str = Query(...),
    start_month: str = Query(..., pattern=PERIOD_PATTERN),
    end_month: str = Query(..., pattern=PERIOD_PATTERN),
    limit: int = Query(10, ge=1, le=100),
    metric: str = Query("apresentada"),
):
    try:
        service = RankingAnalyticsService()
        dataframe = service.get_ranking(
            dimension=dimension,
            start_month=start_month,
            end_month=end_month,
            limit=limit,
            metric=metric,
        )

        return json.loads(
            dataframe.to_json(
                orient="records",
                date_format="iso",
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception("Erro ao consultar ranking.")
        raise HTTPException(
            status_code=500,
            detail="Não foi possível consultar o ranking.",
        ) from exc


@router.get("/summary")
def get_ranking_summary(
    dimension: str = Query(...),
    start_month: str = Query(..., pattern=PERIOD_PATTERN),
    end_month: str = Query(..., pattern=PERIOD_PATTERN),
    metric: str = Query("apresentada"),
):
    try:
        service = RankingAnalyticsService()
        return service.get_ranking_summary(
            dimension=dimension,
            start_month=start_month,
            end_month=end_month,
            metric=metric,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception("Erro ao consultar resumo do ranking.")
        raise HTTPException(
            status_code=500,
            detail="Não foi possível consultar o resumo do ranking.",
        ) from exc


@router.get("/analysis")
def get_ranking_analysis(
    dimension: str = Query(...),
    start_month: str = Query(..., pattern=PERIOD_PATTERN),
    end_month: str = Query(..., pattern=PERIOD_PATTERN),
    limit: int = Query(10, ge=1, le=100),
    metric: str = Query("apresentada"),
):
    try:
        service = RankingAnalyticsService()
        return service.get_ranking_analysis(
            dimension=dimension,
            start_month=start_month,
            end_month=end_month,
            limit=limit,
            metric=metric,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception("Erro ao consultar análise do ranking.")
        raise HTTPException(
            status_code=500,
            detail="Não foi possível consultar a análise do ranking.",
        ) from exc
