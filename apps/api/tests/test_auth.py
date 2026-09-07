from collections.abc import Callable
from urllib.parse import parse_qs, urlparse

import pytest
from app.auth import google
from app.models import AuthSession, User
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

ALLOWED = "partner-a@example.com"
NOT_ALLOWED = "stranger@example.com"


def _start_login(client: TestClient, next_path: str = "/dashboard") -> str:
    """Hit the login endpoint and return the ``state`` value Google would echo."""
    resp = client.get(f"/api/v1/auth/google/login?next={next_path}", follow_redirects=False)
    assert resp.status_code == 302
    location = resp.headers["location"]
    assert location.startswith("https://accounts.google.com/")
    return parse_qs(urlparse(location).query)["state"][0]


def _patch_google(monkeypatch: pytest.MonkeyPatch, *, email: str, verified: bool = True) -> None:
    monkeypatch.setattr(google, "exchange_code", lambda cfg, code: "fake-access-token")
    monkeypatch.setattr(
        google,
        "fetch_userinfo",
        lambda token: google.GoogleUserInfo(
            sub=f"google-{email}", email=email, email_verified=verified, name="Test"
        ),
    )


def test_me_requires_authentication(client: TestClient) -> None:
    assert client.get("/api/v1/auth/me").status_code == 401


def test_callback_allowlisted_creates_session(
    client: TestClient, db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    state = _start_login(client)
    _patch_google(monkeypatch, email=ALLOWED)

    resp = client.get(
        f"/api/v1/auth/google/callback?code=abc&state={state}", follow_redirects=False
    )
    assert resp.status_code == 303
    assert resp.headers["location"] == "http://localhost:3000/dashboard"
    assert client.cookies.get("fm_session")

    me = client.get("/api/v1/auth/me")
    assert me.status_code == 200
    assert me.json()["user"]["email"] == ALLOWED
    assert me.json()["household"] is None
    assert db.execute(select(User).where(User.email == ALLOWED)).scalar_one()


def test_callback_rejects_non_allowlisted_email(
    client: TestClient, db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    state = _start_login(client)
    _patch_google(monkeypatch, email=NOT_ALLOWED)

    resp = client.get(
        f"/api/v1/auth/google/callback?code=abc&state={state}", follow_redirects=False
    )
    assert resp.status_code == 303
    assert resp.headers["location"] == "http://localhost:3000/login?error=not_authorized"
    assert not client.cookies.get("fm_session")
    assert db.execute(select(User)).first() is None
    assert client.get("/api/v1/auth/me").status_code == 401


def test_callback_rejects_tampered_state(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _start_login(client)
    _patch_google(monkeypatch, email=ALLOWED)
    resp = client.get(
        "/api/v1/auth/google/callback?code=abc&state=not-the-real-state",
        follow_redirects=False,
    )
    assert resp.status_code == 400


def test_logout_revokes_session(
    auth_client: Callable[[User], TestClient],
    make_user: Callable[..., User],
    db: Session,
) -> None:
    user = make_user(email=ALLOWED)
    client = auth_client(user)

    assert client.get("/api/v1/auth/me").status_code == 200
    assert client.post("/api/v1/auth/logout").status_code == 204

    session_row = db.execute(select(AuthSession)).scalar_one()
    assert session_row.revoked_at is not None
    assert client.get("/api/v1/auth/me").status_code == 401
