from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration.

    ``app_env`` and ``database_url`` are required and must come from the
    environment / .env file. Everything else is reserved for later phases
    (auth, AI providers, object storage, background jobs) and stays optional
    so Phase 0 can run without them being set.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str
    database_url: str

    # Reserved for later phases (Google OAuth - Phase 1)
    google_client_id: str | None = None
    google_client_secret: str | None = None

    # Reserved for later phases (Financial AI - Phase 9)
    llm_provider: str | None = None
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    embedding_provider: str | None = None

    # Reserved for later phases (Telegram - Phase 11)
    telegram_bot_token: str | None = None

    # Reserved for later phases (Document ingestion / object storage)
    object_storage_endpoint: str | None = None
    object_storage_bucket: str | None = None
    object_storage_access_key: str | None = None
    object_storage_secret_key: str | None = None

    # Reserved for later phases (async worker / job queue)
    redis_url: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
