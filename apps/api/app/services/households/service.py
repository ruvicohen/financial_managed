"""Household creation, membership, and the second-partner invitation flow.

This project is a closed two-person system: authentication is already gated by
an email allowlist, so the household is simply capped at two members. Partner A
(the creator) is ``OWNER``/``PARTNER_A``; Partner B joins with a one-time invite
link and becomes ``MEMBER``/``PARTNER_B``.
"""

import hashlib
import secrets
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.dependencies import HouseholdContext
from app.models import (
    Household,
    HouseholdInvitation,
    HouseholdMembership,
    MembershipRole,
    PartnerLabel,
    User,
)

MAX_MEMBERS = 2
INVITE_TTL = timedelta(days=7)


def _hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def _aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=UTC)


@dataclass(frozen=True)
class InvitationResult:
    invitation: HouseholdInvitation
    raw_token: str


class HouseholdService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _membership_for(self, user_id: uuid.UUID) -> HouseholdMembership | None:
        return self.db.execute(
            select(HouseholdMembership).where(HouseholdMembership.user_id == user_id)
        ).scalar_one_or_none()

    def _member_count(self, household_id: uuid.UUID) -> int:
        return int(
            self.db.execute(
                select(func.count())
                .select_from(HouseholdMembership)
                .where(HouseholdMembership.household_id == household_id)
            ).scalar_one()
        )

    def list_members(self, household_id: uuid.UUID) -> list[HouseholdMembership]:
        return list(
            self.db.execute(
                select(HouseholdMembership)
                .where(HouseholdMembership.household_id == household_id)
                .order_by(HouseholdMembership.partner_label)
            ).scalars()
        )

    def provision_for_user(self, user: User, name: str) -> Household:
        if self._membership_for(user.id) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already belongs to a household",
            )
        household = Household(name=name.strip() or "Household", created_by_user_id=user.id)
        self.db.add(household)
        self.db.flush()
        self.db.add(
            HouseholdMembership(
                household_id=household.id,
                user_id=user.id,
                partner_label=PartnerLabel.PARTNER_A,
                role=MembershipRole.OWNER,
            )
        )
        self.db.flush()
        return household

    def create_invitation(self, ctx: HouseholdContext) -> InvitationResult:
        if ctx.membership.role != MembershipRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the household owner can invite",
            )
        if self._member_count(ctx.household_id) >= MAX_MEMBERS:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Household is already full"
            )
        now = datetime.now(UTC)
        pending = self.db.execute(
            select(HouseholdInvitation).where(
                HouseholdInvitation.household_id == ctx.household_id,
                HouseholdInvitation.accepted_at.is_(None),
                HouseholdInvitation.expires_at > now,
            )
        ).scalar_one_or_none()
        if pending is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An invitation is already pending",
            )
        raw_token = secrets.token_urlsafe(32)
        invitation = HouseholdInvitation(
            household_id=ctx.household_id,
            token_hash=_hash_token(raw_token),
            created_by_user_id=ctx.user.id,
            expires_at=now + INVITE_TTL,
        )
        self.db.add(invitation)
        self.db.flush()
        return InvitationResult(invitation=invitation, raw_token=raw_token)

    def accept_invitation(self, user: User, raw_token: str) -> HouseholdMembership:
        invitation = self.db.execute(
            select(HouseholdInvitation).where(
                HouseholdInvitation.token_hash == _hash_token(raw_token)
            )
        ).scalar_one_or_none()
        if invitation is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid invitation"
            )
        if invitation.accepted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invitation has already been used",
            )
        if _aware(invitation.expires_at) <= datetime.now(UTC):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invitation has expired"
            )
        if self._membership_for(user.id) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already belongs to a household",
            )
        if self._member_count(invitation.household_id) >= MAX_MEMBERS:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Household is already full"
            )
        membership = HouseholdMembership(
            household_id=invitation.household_id,
            user_id=user.id,
            partner_label=PartnerLabel.PARTNER_B,
            role=MembershipRole.MEMBER,
        )
        self.db.add(membership)
        invitation.accepted_at = datetime.now(UTC)
        invitation.accepted_by_user_id = user.id
        self.db.flush()
        return membership
