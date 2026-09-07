import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, uuid_pk

if TYPE_CHECKING:
    from app.models.user import User


class PartnerLabel(enum.StrEnum):
    PARTNER_A = "PARTNER_A"
    PARTNER_B = "PARTNER_B"


class MembershipRole(enum.StrEnum):
    OWNER = "OWNER"
    MEMBER = "MEMBER"


class HouseholdMembership(TimestampMixin, Base):
    __tablename__ = "household_memberships"
    __table_args__ = (
        UniqueConstraint("household_id", "user_id", name="uq_membership_household_user"),
        UniqueConstraint(
            "household_id", "partner_label", name="uq_membership_household_partner_label"
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    household_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("households.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    partner_label: Mapped[PartnerLabel] = mapped_column(
        Enum(PartnerLabel, name="partner_label"), nullable=False
    )
    role: Mapped[MembershipRole] = mapped_column(
        Enum(MembershipRole, name="membership_role"), nullable=False
    )

    user: Mapped["User"] = relationship("User", lazy="joined")
