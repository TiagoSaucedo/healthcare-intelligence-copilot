
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=3,
        max_length=2000,
        description="Pergunta enviada ao Healthcare Intelligence Copilot",
    )


class ChatResponse(BaseModel):
    answer: str


@router.post("", response_model=ChatResponse)
def chat(request: Request, payload: ChatRequest):
    try:
        agent = request.app.state.analytics_agent

        result = agent.invoke({
            "messages": [
                {"role": "user", "content": payload.message}
            ]
        })

        answer = result["messages"][-1].content

        return JSONResponse(
            content={"answer": answer},
            media_type="application/json; charset=utf-8",
        )

    except Exception as exc:
        logger.exception("Erro ao processar solicitação de chat.")

        raise HTTPException(
            status_code=500,
            detail="Não foi possível processar a pergunta.",
        ) from exc
