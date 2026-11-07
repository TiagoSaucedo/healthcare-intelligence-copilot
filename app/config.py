
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str

    llm_provider: str = "ollama"

    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"

    ollama_model: str = "llama3.1:8b"
    ollama_base_url: str = "http://localhost:11434"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
