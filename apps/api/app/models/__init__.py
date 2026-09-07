"""ORM models.

Importing this package registers every model on ``Base.metadata`` so Alembic
autogenerate and ``create_all`` see the full schema.
"""

from app.models.household import Household
from app.models.invitation import HouseholdInvitation
from app.models.membership import HouseholdMembership, MembershipRole, PartnerLabel
from app.models.session import AuthSession
from app.models.user import User

__all__ = [
    "AuthSession",
    "Household",
    "HouseholdInvitation",
    "HouseholdMembership",
    "MembershipRole",
    "PartnerLabel",
    "User",
]
