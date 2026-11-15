import json
import logging

from fastapi import APIRouter, HTTPException, Query

from app.analytics.services.contract_service import (
    ContractAnalyticsService,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/analytics/contracts",
    tags=["Contract Analytics"],
)

PERIOD_PATTERN = r"^\d{4}-(0[1-9]|1[0-2])$"


@router.get("/summary")
def get_contract_summary(
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
        service = ContractAnalyticsService()
        return service.get_contract_summary(
            start_month,
            end_month,
        )

    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    except Exception as exc:
        logger.exception("Erro ao consultar o resumo de contratos.")
        raise HTTPException(
            status_code=500,
            detail="Não foi possível consultar o resumo de contratos.",
        ) from exc


@router.get("/monthly")
def get_contract_overview(
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
        service = ContractAnalyticsService()
        dataframe = service.get_contract_by_period(
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
        logger.exception("Erro ao consultar despesas por contrato.")
        raise HTTPException(
            status_code=500,
            detail="Não foi possível consultar despesas por contrato.",
        ) from exc
