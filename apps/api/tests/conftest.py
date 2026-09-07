import os
import uuid
from collections.abc import Callable, Iterator
from datetime import UTC, datetime, timedelta

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault(
    "DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/financial_managed"
)
os.environ.setdefault("SESSION_SECRET", "test-session-secret")
os.environ.setdefault("GOOGLE_CLIENT_ID", "test-client-id")
os.environ.setdefault("GOOGLE_CLIENT_SECRET", "test-client-secret")
os.environ.setdefault("FRONTEND_URL", "http://localhost:3000")
os.environ.setdefault("COOKIE_SECURE", "false")
os.environ.setdefault("ALLOWED_GOOGLE_EMAILS", "partner-a@example.com,partner-b@example.com")

import pytest
from alembic import command
from alembic.config import Config
from app.auth.sessions import hash_token
from app.db.session import get_db, get_engine
from app.main import create_app
from app.models import AuthSession, User
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

API_DIR = os.path.dirname(os.path.dirname(__file__))


@pytest.fixture(scope="session", autouse=True)
def _migrated_database() -> None:
    """Bring the configured database up to head once for the whole test run."""
    cfg = Config()
    cfg.set_main_option("script_location", os.path.join(API_DIR, "alembic"))
    cfg.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])
    command.upgrade(cfg, "head")


@pytest.fixture
def db() -> Iterator[Session]:
    """A session wrapped in an outer transaction that is rolled back per test.

    ``join_transaction_mode="create_savepoint"`` lets application code call
    ``session.commit()`` (the routers do) without ending the outer transaction,
    so every test still starts from a clean database.
    """
    connection = get_engine().connect()
    outer = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    try:
        yield session
    finally:
        session.close()
        outer.rollback()
        connection.close()


def _build_client(db: Session) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_db] = lambda: db
    return TestClient(app)


@pytest.fixture
def client(db: Session) -> Iterator[TestClient]:
    with _build_client(db) as test_client:
        yield test_client


@pytest.fixture
def make_user(db: Session) -> Callable[..., User]:
    def _make(email: str | None = None, name: str = "Test User") -> User:
        suffix = uuid.uuid4().hex[:8]
        user = User(
            google_sub=f"sub-{suffix}",
            email=(email or f"user-{suffix}@example.com").lower(),
            name=name,
        )
        db.add(user)
        db.flush()
        return user

    return _make


@pytest.fixture
def auth_client(db: Session) -> Iterator[Callable[[User], TestClient]]:
    """Build a fresh TestClient carrying a valid session cookie for ``user``.

    Each call returns an independent client (its own cookie jar) bound to the
    same transactional session, so a test can act as two different users
    without their sessions bleeding into each other.
    """
    created: list[TestClient] = []

    def _for(user: User) -> TestClient:
        raw_token = uuid.uuid4().hex + uuid.uuid4().hex
        db.add(
            AuthSession(
                user_id=user.id,
                token_hash=hash_token(raw_token),
                expires_at=datetime.now(UTC) + timedelta(days=30),
            )
        )
        db.flush()
        test_client = _build_client(db)
        test_client.cookies.set("fm_session", raw_token)
        created.append(test_client)
        return test_client

    yield _for
    for test_client in created:
        test_client.close()
