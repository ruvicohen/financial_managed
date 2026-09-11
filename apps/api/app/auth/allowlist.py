from app.config import get_settings


def is_email_allowed(email: str) -> bool:
    """True only if ``email`` is on ``ALLOWED_GOOGLE_EMAILS`` (fail closed)."""
    allowed = get_settings().allowed_emails
    return bool(allowed) and email.strip().lower() in allowed
