import logging
import secrets
from datetime import UTC, datetime
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.households import build_household_out
from app.auth import google
from app.auth.allowlist import is_email_allowed
from app.auth.config import AuthConfig, require_auth_config
from app.auth.dependencies import OptionalUser
from app.auth.sessions import create_session, revoke_session
from app.auth.state import OAuthState, dumps, loads
from app.config import get_settings
from app.db.session import get_db
from app.models import HouseholdMembership, User
from app.schemas.auth import MeOut, UserOut

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

DbSession = Annotated[Session, Depends(get_db)]


def _safe_next(value: str | None) -> str:
    if value and value.startswith("/") and not value.startswith("//"):
        return value
    return "/dashboard"


def _set_session_cookie(response: Response, raw_token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        key=settings.session_cookie_name,
        value=raw_token,
        max_age=settings.session_ttl_hours * 3600,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )


def _clear_cookie(response: Response, name: str) -> None:
    response.delete_cookie(name, path="/")


def _login_error_redirect(cfg: AuthConfig, code: str) -> RedirectResponse:
    resp = RedirectResponse(
        url=f"{cfg.frontend_url}/login?error={code}", status_code=status.HTTP_303_SEE_OTHER
    )
    _clear_cookie(resp, get_settings().oauth_cookie_name)
    return resp


@router.get("/google/login")
def google_login(request: Request, next: str | None = None) -> RedirectResponse:
    cfg = require_auth_config()
    state = secrets.token_urlsafe(16)
    nonce = secrets.token_urlsafe(16)
    oauth_state = OAuthState(state=state, nonce=nonce, next=_safe_next(next))
    redirect = RedirectResponse(
        url=google.authorization_url(cfg, state=state, nonce=nonce),
        status_code=status.HTTP_302_FOUND,
    )
    redirect.set_cookie(
        key=get_settings().oauth_cookie_name,
        value=dumps(cfg.session_secret, oauth_state),
        max_age=600,
        httponly=True,
        secure=get_settings().cookie_secure,
        samesite="lax",
        path="/",
    )
    return redirect


@router.get("/google/callback")
def google_callback(
    request: Request,
    db: DbSession,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
) -> RedirectResponse:
    cfg = require_auth_config()

    if error or not code or not state:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OAuth failed")

    raw_state_cookie = request.cookies.get(get_settings().oauth_cookie_name)
    oauth_state = loads(cfg.session_secret, raw_state_cookie) if raw_state_cookie else None
    if oauth_state is None or not secrets.compare_digest(oauth_state.state, state):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OAuth state")

    try:
        access_token = google.exchange_code(cfg, code)
        info = google.fetch_userinfo(access_token)
    except (httpx.HTTPError, ValueError):
        logger.exception("Google OAuth exchange failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail="Google sign-in failed"
        ) from None

    email = info.email.strip().lower()
    if not info.email_verified or not is_email_allowed(email):
        logger.warning("Rejected sign-in for non-authorized account")
        return _login_error_redirect(cfg, "not_authorized")

    user = db.execute(select(User).where(User.google_sub == info.sub)).scalar_one_or_none()
    if user is None:
        user = User(google_sub=info.sub, email=email)
        db.add(user)
    user.email = email
    user.name = info.name or user.name
    user.picture_url = info.picture
    user.last_login_at = datetime.now(UTC)
    db.flush()

    raw_token = create_session(db, user, user_agent=request.headers.get("user-agent"))
    db.commit()

    redirect = RedirectResponse(
        url=f"{cfg.frontend_url}{oauth_state.next}", status_code=status.HTTP_303_SEE_OTHER
    )
    _set_session_cookie(redirect, raw_token)
    _clear_cookie(redirect, get_settings().oauth_cookie_name)
    return redirect


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, db: DbSession) -> Response:
    token = request.cookies.get(get_settings().session_cookie_name)
    if token:
        revoke_session(db, token)
        db.commit()
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    _clear_cookie(response, get_settings().session_cookie_name)
    return response


@router.get("/me", response_model=MeOut)
def me(user: OptionalUser, db: DbSession) -> MeOut:
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    membership = db.execute(
        select(HouseholdMembership).where(HouseholdMembership.user_id == user.id)
    ).scalar_one_or_none()
    household_out = None
    if membership is not None:
        household_out = build_household_out(db, membership.household_id)
    return MeOut(user=UserOut.model_validate(user), household=household_out)
