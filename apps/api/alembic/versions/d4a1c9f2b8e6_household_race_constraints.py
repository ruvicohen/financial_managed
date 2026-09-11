"""household membership/invite race-condition constraints

Revision ID: d4a1c9f2b8e6
Revises: b7f3c1d20a41
Create Date: 2026-09-11 00:00:00

Backs two invariants that were previously enforced only by a check-then-insert
in application code, so a race between concurrent requests could violate them:
a user belongs to at most one household, and a household has at most one
active (unaccepted) invitation at a time.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d4a1c9f2b8e6"
down_revision: str | None = "b7f3c1d20a41"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_unique_constraint("uq_membership_user_id", "household_memberships", ["user_id"])
    op.create_index(
        "uq_invitations_active_per_household",
        "household_invitations",
        ["household_id"],
        unique=True,
        postgresql_where=sa.text("accepted_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_invitations_active_per_household",
        table_name="household_invitations",
        postgresql_where=sa.text("accepted_at IS NULL"),
    )
    op.drop_constraint("uq_membership_user_id", "household_memberships", type_="unique")
