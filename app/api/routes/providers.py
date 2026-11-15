import json
import logging

from fastapi import APIRouter, HTTPException, Query

from app.analytics.services.provider_service import ProviderAnalyticsService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/analytics/providers",
    tags=["Provider Analytics"],
)

PERIOD_PATTERN = r"^\d{4}-(0[1-9]|1[0-2])$"


@router.get("/summary")
def get_provider_summary(
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
        service = ProviderAnalyticsService()
        return service.get_provider_summary(start_month, end_month)

    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    except Exception as exc:
        logger.exception("Erro ao consultar o resumo de prestadores.")
        raise HTTPException(
            status_code=500,
            detail="Não foi possível consultar o resumo de prestadores.",
        ) from exc


@router.get("/monthly")
def get_provider_overview(
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
        service = ProviderAnalyticsService()
        dataframe = service.get_provider_by_period(
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
        logger.exception("Erro ao consultar despesas por prestador.")
        raise HTTPException(
            status_code=500,
            detail="Não foi possível consultar despesas por prestador.",
        ) from exc


@router.get("/paid/summary")
def get_paid_provider_summary(
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
        service = ProviderAnalyticsService()
        return service.get_paid_provider_summary(
            start_month,
            end_month,
        )

    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    except Exception as exc:
        logger.exception("Erro ao consultar o resumo financeiro por prestador.")
        raise HTTPException(
            status_code=500,
            detail="Não foi possível consultar o resumo financeiro por prestador.",
        ) from exc


@router.get("/paid/monthly")
def get_paid_provider_overview(
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
        service = ProviderAnalyticsService()
        dataframe = service.get_paid_provider_by_period(
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
        logger.exception("Erro ao consultar pagamentos por prestador.")
        raise HTTPException(
            status_code=500,
            detail="Não foi possível consultar pagamentos por prestador.",
        ) from exc
