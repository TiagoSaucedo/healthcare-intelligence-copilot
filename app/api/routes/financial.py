import json
import logging

from fastapi import APIRouter, HTTPException, Query

from app.analytics.services.financial_service import FinancialAnalyticsService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/analytics/financial",
    tags=["Financial Analytics"],
)

PERIOD_PATTERN = r"^\d{4}-(0[1-9]|1[0-2])$"


@router.get("/summary")
def get_financial_summary(
    start_month: str = Query(..., pattern=PERIOD_PATTERN, description="Mês inicial no formato YYYY-MM"),
    end_month: str = Query(..., pattern=PERIOD_PATTERN, description="Mês final no formato YYYY-MM"),
):
    try:
        service = FinancialAnalyticsService()
        return service.get_financial_summary(start_month, end_month)

    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    except Exception as exc:
        logger.exception("Erro ao consultar o resumo financeiro.")
        raise HTTPException(
            status_code=500,
            detail="Não foi possível consultar o resumo financeiro.",
        ) from exc


@router.get("/monthly")
def get_monthly_financial_overview(
    start_month: str = Query(..., pattern=PERIOD_PATTERN, description="Mês inicial no formato YYYY-MM"),
    end_month: str = Query(..., pattern=PERIOD_PATTERN, description="Mês final no formato YYYY-MM"),
):
    try:
        service = FinancialAnalyticsService()
        dataframe = service.get_monthly_overview_by_period(
            start_month,
            end_month,
        )
        return json.loads(
            dataframe.to_json(
                orient="records",
                date_format="iso",
            )
        )

    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    except Exception as exc:
        logger.exception("Erro ao consultar o histórico financeiro mensal.")
        raise HTTPException(
            status_code=500,
            detail="Não foi possível consultar o histórico financeiro mensal.",
        ) from exc
