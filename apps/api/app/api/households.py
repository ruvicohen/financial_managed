import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.config import require_auth_config
from app.auth.dependencies import CurrentUser, HouseholdCtx
from app.db.session import get_db
from app.models import Household
from app.schemas.household import (
    AcceptInvitationIn,
    CreateHouseholdIn,
    HouseholdOut,
    InvitationOut,
    MemberOut,
)
from app.services.households import HouseholdService

router = APIRouter(prefix="/households", tags=["households"])

DbSession = Annotated[Session, Depends(get_db)]


def build_household_out(db: Session, household_id: uuid.UUID) -> HouseholdOut:
    household = db.get(Household, household_id)
    assert household is not None
    members = HouseholdService(db).list_members(household_id)
    return HouseholdOut(
        id=household.id,
        name=household.name,
        members=[
            MemberOut(
                user_id=m.user_id,
                email=m.user.email,
                name=m.user.name,
                partner_label=m.partner_label,
                role=m.role,
            )
            for m in members
        ],
    )


@router.post("", response_model=HouseholdOut, status_code=201)
def create_household(body: CreateHouseholdIn, user: CurrentUser, db: DbSession) -> HouseholdOut:
    household = HouseholdService(db).provision_for_user(user, body.name)
    db.commit()
    return build_household_out(db, household.id)


@router.get("/current", response_model=HouseholdOut)
def get_current_household(ctx: HouseholdCtx, db: DbSession) -> HouseholdOut:
    return build_household_out(db, ctx.household_id)


@router.post("/current/invitations", response_model=InvitationOut, status_code=201)
def create_invitation(ctx: HouseholdCtx, db: DbSession) -> InvitationOut:
    cfg = require_auth_config()
    result = HouseholdService(db).create_invitation(ctx)
    db.commit()
    return InvitationOut(
        token=result.raw_token,
        invite_url=f"{cfg.frontend_url}/join?token={result.raw_token}",
        expires_at=result.invitation.expires_at,
    )


@router.post("/invitations/accept", response_model=HouseholdOut, status_code=201)
def accept_invitation(body: AcceptInvitationIn, user: CurrentUser, db: DbSession) -> HouseholdOut:
    membership = HouseholdService(db).accept_invitation(user, body.token)
    db.commit()
    return build_household_out(db, membership.household_id)
