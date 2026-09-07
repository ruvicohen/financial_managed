from app.config import Settings


def test_bare_postgresql_url_gets_psycopg_driver() -> None:
    settings = Settings(app_env="test", database_url="postgresql://user:pw@host:5432/db")
    assert settings.database_url == "postgresql+psycopg://user:pw@host:5432/db"


def test_legacy_postgres_scheme_gets_psycopg_driver() -> None:
    settings = Settings(app_env="test", database_url="postgres://user:pw@host:5432/db")
    assert settings.database_url == "postgresql+psycopg://user:pw@host:5432/db"


def test_explicit_driver_is_left_unchanged() -> None:
    url = "postgresql+psycopg://user:pw@host:5432/db"
    settings = Settings(app_env="test", database_url=url)
    assert settings.database_url == url
