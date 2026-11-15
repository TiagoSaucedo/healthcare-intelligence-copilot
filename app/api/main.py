from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.agents.analytics_agent import create_analytics_agent
from app.api.routes.chat import router as chat_router
from app.api.routes.contracts import router as contracts_router
from app.api.routes.financial import router as financial_router
from app.api.routes.procedures import router as procedures_router
from app.api.routes.providers import router as providers_router
from app.api.routes.rankings import router as rankings_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.analytics_agent = create_analytics_agent()
    yield
    app.state.analytics_agent = None


app = FastAPI(
    title="Healthcare Intelligence Copilot",
    description="API para análise financeira e assistencial em operadoras de saúde.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(
    chat_router,
    prefix="/api/v1",
)

app.include_router(
    financial_router,
    prefix="/api/v1",
)

app.include_router(
    providers_router,
    prefix="/api/v1",
)

app.include_router(
    procedures_router,
    prefix="/api/v1",
)

app.include_router(
    contracts_router,
    prefix="/api/v1",
)

app.include_router(
    rankings_router,
    prefix="/api/v1",
)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "healthcare-intelligence-copilot",
    }
