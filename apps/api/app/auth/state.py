"""Signed, short-lived OAuth state carried in the ``fm_oauth`` cookie.

Protects the callback against CSRF / fixation: the ``state`` returned by Google
must match the signed value we set before the redirect.
"""

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from pydantic import BaseModel

_SALT = "fm-oauth-state"
MAX_AGE_SECONDS = 600  # 10 minutes to complete the Google round-trip


class OAuthState(BaseModel):
    state: str
    nonce: str
    next: str = "/dashboard"


def _serializer(secret: str) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(secret, salt=_SALT)


def dumps(secret: str, payload: OAuthState) -> str:
    return _serializer(secret).dumps(payload.model_dump())


def loads(secret: str, token: str) -> OAuthState | None:
    try:
        raw = _serializer(secret).loads(token, max_age=MAX_AGE_SECONDS)
    except (BadSignature, SignatureExpired):
        return None
    try:
        return OAuthState.model_validate(raw)
    except ValueError:
        return None
