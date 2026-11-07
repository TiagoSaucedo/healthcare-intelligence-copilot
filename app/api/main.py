
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.agents.analytics_agent import create_analytics_agent
from app.api.routes.chat import router as chat_router


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


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "healthcare-intelligence-copilot",
    }
