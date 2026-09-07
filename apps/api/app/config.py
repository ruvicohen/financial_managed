from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration.

    ``app_env`` and ``database_url`` are required and must come from the
    environment / .env file. The Google OAuth / session values are required
    once authentication is exercised (Phase 1) but stay optional here so
    ``/health`` and migrations still work before OAuth is configured; the auth
    router validates them lazily via :func:`app.auth.config.require_auth_config`.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str
    database_url: str

    @field_validator("database_url")
    @classmethod
    def _use_psycopg_driver(cls, v: str) -> str:
        """Normalize managed-Postgres connection strings to the psycopg3 driver.

        Providers like Render hand out bare ``postgres://``/``postgresql://``
        URLs. SQLAlchemy defaults a driverless ``postgresql://`` scheme to
        the legacy psycopg2 dialect, which isn't installed here (only
        ``psycopg[binary]`` v3 is) - without this, /ready fails at runtime
        with "No module named 'psycopg2'" even though the app works locally
        where .env already spells out ``+psycopg`` explicitly.
        """
        if v.startswith("postgres://"):
            v = "postgresql://" + v[len("postgres://") :]
        if v.startswith("postgresql://"):
            v = "postgresql+psycopg://" + v[len("postgresql://") :]
        return v

    # --- Auth / Google OAuth (Phase 1) ---
    google_client_id: str | None = None
    google_client_secret: str | None = None
    google_redirect_uri: str = "http://localhost:8000/api/v1/auth/google/callback"
    frontend_url: str = "http://localhost:3000"
    # Signs the short-lived OAuth state/nonce cookie. Required for auth.
    session_secret: str | None = None
    # Comma-separated allowlist of Google account emails permitted to sign in.
    # Empty => deny everyone (fail closed).
    allowed_google_emails: str = ""

    # Session cookie behaviour (defaults are fine; override only if needed).
    session_cookie_name: str = "fm_session"
    oauth_cookie_name: str = "fm_oauth"
    session_ttl_hours: int = 720
    cookie_secure: bool = True

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

    @property
    def allowed_emails(self) -> set[str]:
        return {
            part.strip().lower() for part in self.allowed_google_emails.split(",") if part.strip()
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
