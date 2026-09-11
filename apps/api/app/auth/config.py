from dataclasses import dataclass

from fastapi import HTTPException, status

from app.config import get_settings


@dataclass(frozen=True)
class AuthConfig:
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str
    session_secret: str
    frontend_url: str


def require_auth_config() -> AuthConfig:
    """Return the auth settings, or raise 503 if the deployment hasn't set them.

    Kept lazy (not validated at import/startup) so ``/health`` and migrations
    still work on an environment where OAuth is not configured yet.
    """
    s = get_settings()
    missing = [
        name
        for name, value in (
            ("GOOGLE_CLIENT_ID", s.google_client_id),
            ("GOOGLE_CLIENT_SECRET", s.google_client_secret),
            ("SESSION_SECRET", s.session_secret),
        )
        if not value
    ]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Authentication is not configured (missing: {', '.join(missing)}).",
        )
    assert s.google_client_id and s.google_client_secret and s.session_secret
    return AuthConfig(
        google_client_id=s.google_client_id,
        google_client_secret=s.google_client_secret,
        google_redirect_uri=s.google_redirect_uri,
        session_secret=s.session_secret,
        frontend_url=s.frontend_url.rstrip("/"),
    )
