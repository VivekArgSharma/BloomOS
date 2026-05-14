from functools import lru_cache  # noqa: F401 (kept for future use)
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="development", alias="APP_ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    frontend_url: str = Field(default="http://localhost:5173", alias="FRONTEND_URL")

    supabase_url: str = Field(default="", alias="SUPABASE_URL")
    supabase_anon_key: str = Field(default="", alias="SUPABASE_ANON_KEY")
    supabase_service_role_key: str = Field(default="", alias="SUPABASE_SERVICE_ROLE_KEY")

    # OpenRouter LLM settings
    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    openrouter_model: str = Field(default="nvidia/nemotron-nano-8b-v1:free", alias="OPENROUTER_MODEL")
    openrouter_timeout: int = Field(default=60, alias="OPENROUTER_TIMEOUT")
    openweathermap_api_key: str = Field(default="", alias="OPENWEATHERMAP_API_KEY")
    redis_url: str | None = Field(default=None, alias="REDIS_URL")
    supabase_storage_bucket: str = Field(default="plant-photos", alias="SUPABASE_STORAGE_BUCKET")
    max_upload_bytes: int = Field(default=6_000_000, alias="MAX_UPLOAD_BYTES")

    rag_docs_path: Path = Field(default=Path("./data/rag_docs"), alias="RAG_DOCS_PATH")
    faiss_index_path: Path = Field(default=Path("./data/faiss_index"), alias="FAISS_INDEX_PATH")
    use_mock_data: bool = Field(default=True, alias="USE_MOCK_DATA")


def get_settings() -> Settings:
    return Settings()
