"""Minimal Google OpenID Connect (authorization-code) client.

Only what Phase 1 needs: build the consent URL, exchange the code for tokens,
and read the userinfo endpoint. Endpoints are the stable well-known Google URLs
rather than a runtime discovery-document fetch.
"""

from urllib.parse import urlencode

import httpx
from pydantic import BaseModel

from app.auth.config import AuthConfig

AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"  # noqa: S105 (public URL, not a secret)
USERINFO_ENDPOINT = "https://openidconnect.googleapis.com/v1/userinfo"

SCOPES = "openid email profile"
_TIMEOUT = httpx.Timeout(10.0)


class GoogleUserInfo(BaseModel):
    sub: str
    email: str
    email_verified: bool = False
    name: str = ""
    picture: str | None = None


def authorization_url(cfg: AuthConfig, *, state: str, nonce: str) -> str:
    params = {
        "client_id": cfg.google_client_id,
        "redirect_uri": cfg.google_redirect_uri,
        "response_type": "code",
        "scope": SCOPES,
        "state": state,
        "nonce": nonce,
        "access_type": "online",
        "prompt": "select_account",
    }
    return f"{AUTH_ENDPOINT}?{urlencode(params)}"


def exchange_code(cfg: AuthConfig, code: str) -> str:
    """Exchange an authorization code for an access token; returns the token."""
    with httpx.Client(timeout=_TIMEOUT) as client:
        resp = client.post(
            TOKEN_ENDPOINT,
            data={
                "code": code,
                "client_id": cfg.google_client_id,
                "client_secret": cfg.google_client_secret,
                "redirect_uri": cfg.google_redirect_uri,
                "grant_type": "authorization_code",
            },
        )
    resp.raise_for_status()
    access_token = resp.json().get("access_token")
    if not access_token:
        raise ValueError("Google token response did not contain an access_token")
    return str(access_token)


def fetch_userinfo(access_token: str) -> GoogleUserInfo:
    with httpx.Client(timeout=_TIMEOUT) as client:
        resp = client.get(USERINFO_ENDPOINT, headers={"Authorization": f"Bearer {access_token}"})
    resp.raise_for_status()
    return GoogleUserInfo.model_validate(resp.json())
