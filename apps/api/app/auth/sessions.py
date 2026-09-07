"""DB-backed opaque sessions.

A random token lives in the ``fm_session`` httpOnly cookie; only its SHA-256
hash is stored, in ``auth_sessions``, with an expiry and a nullable
``revoked_at`` so logout is a real revocation.
"""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import AuthSession, User


def hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def create_session(db: Session, user: User, *, user_agent: str | None = None) -> str:
    raw_token = secrets.token_urlsafe(32)
    ttl = timedelta(hours=get_settings().session_ttl_hours)
    db.add(
        AuthSession(
            user_id=user.id,
            token_hash=hash_token(raw_token),
            expires_at=datetime.now(UTC) + ttl,
            user_agent=(user_agent or None) and user_agent[:512],
        )
    )
    db.flush()
    return raw_token


def resolve_session(db: Session, raw_token: str) -> User | None:
    row = db.execute(
        select(AuthSession).where(AuthSession.token_hash == hash_token(raw_token))
    ).scalar_one_or_none()
    if row is None or row.revoked_at is not None:
        return None
    expires_at = row.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    if expires_at <= datetime.now(UTC):
        return None
    return db.get(User, row.user_id)


def revoke_session(db: Session, raw_token: str) -> None:
    row = db.execute(
        select(AuthSession).where(AuthSession.token_hash == hash_token(raw_token))
    ).scalar_one_or_none()
    if row is not None and row.revoked_at is None:
        row.revoked_at = datetime.now(UTC)
        db.flush()
