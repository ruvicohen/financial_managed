import uuid
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.sessions import resolve_session
from app.config import get_settings
from app.db.session import get_db
from app.models import HouseholdMembership, User


def get_optional_user(request: Request, db: Annotated[Session, Depends(get_db)]) -> User | None:
    token = request.cookies.get(get_settings().session_cookie_name)
    if not token:
        return None
    return resolve_session(db, token)


def get_current_user(
    user: Annotated[User | None, Depends(get_optional_user)],
) -> User:
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[User | None, Depends(get_optional_user)]


@dataclass(frozen=True)
class HouseholdContext:
    household_id: uuid.UUID
    user: User
    membership: HouseholdMembership


def get_household_context(
    user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> HouseholdContext:
    membership = db.execute(
        select(HouseholdMembership).where(HouseholdMembership.user_id == user.id)
    ).scalar_one_or_none()
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a member of any household",
        )
    return HouseholdContext(household_id=membership.household_id, user=user, membership=membership)


HouseholdCtx = Annotated[HouseholdContext, Depends(get_household_context)]
