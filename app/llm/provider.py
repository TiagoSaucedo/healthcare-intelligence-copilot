
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from app.config import settings


def get_chat_model():
    """
    Cria o modelo de linguagem conforme o provedor configurado.

    Provedores suportados:
    - openai
    - ollama
    """
    provider = settings.llm_provider.lower()

    if provider == "openai":
        if not settings.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY não foi configurada."
            )

        return ChatOpenAI(
            model=settings.openai_model,
            api_key=SecretStr(settings.openai_api_key),
            temperature=0,
        )

    if provider == "ollama":
        return ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=0,
        )

    raise ValueError(
        f"Provedor LLM não suportado: {provider}. "
        "Utilize 'openai' ou 'ollama'."
    )
