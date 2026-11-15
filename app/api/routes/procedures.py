import json
import logging

from fastapi import APIRouter, HTTPException, Query

from app.analytics.services.procedure_service import (
    ProcedureAnalyticsService,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/analytics/procedures",
    tags=["Procedure Analytics"],
)

PERIOD_PATTERN = r"^\d{4}-(0[1-9]|1[0-2])$"


@router.get("/summary")
def get_procedure_summary(
    start_month: str = Query(
        ...,
        pattern=PERIOD_PATTERN,
        description="Mês inicial no formato YYYY-MM",
    ),
    end_month: str = Query(
        ...,
        pattern=PERIOD_PATTERN,
        description="Mês final no formato YYYY-MM",
    ),
):
    try:
        service = ProcedureAnalyticsService()
        return service.get_procedure_summary(
            start_month,
            end_month,
        )

    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    except Exception as exc:
        logger.exception("Erro ao consultar o resumo de procedimentos.")
        raise HTTPException(
            status_code=500,
            detail="Não foi possível consultar o resumo de procedimentos.",
        ) from exc


@router.get("/monthly")
def get_procedure_overview(
    start_month: str = Query(
        ...,
        pattern=PERIOD_PATTERN,
        description="Mês inicial no formato YYYY-MM",
    ),
    end_month: str = Query(
        ...,
        pattern=PERIOD_PATTERN,
        description="Mês final no formato YYYY-MM",
    ),
):
    try:
        service = ProcedureAnalyticsService()
        dataframe = service.get_procedure_by_period(
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
        logger.exception("Erro ao consultar despesas por procedimento.")
        raise HTTPException(
            status_code=500,
            detail="Não foi possível consultar despesas por procedimento.",
        ) from exc
