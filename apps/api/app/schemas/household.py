import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models import MembershipRole, PartnerLabel


class MemberOut(BaseModel):
    user_id: uuid.UUID
    email: str
    name: str
    partner_label: PartnerLabel
    role: MembershipRole


class HouseholdOut(BaseModel):
    id: uuid.UUID
    name: str
    members: list[MemberOut] = Field(default_factory=list)


class CreateHouseholdIn(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class InvitationOut(BaseModel):
    token: str
    invite_url: str
    expires_at: datetime


class AcceptInvitationIn(BaseModel):
    token: str = Field(min_length=1)
