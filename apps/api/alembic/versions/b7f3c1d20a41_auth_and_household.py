"""auth and household

Revision ID: b7f3c1d20a41
Revises: a52b418abefe
Create Date: 2026-09-07 00:00:00

Phase 1: users, households, memberships, invitations, auth sessions.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b7f3c1d20a41"
down_revision: str | None = "a52b418abefe"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

partner_label = sa.Enum("PARTNER_A", "PARTNER_B", name="partner_label")
membership_role = sa.Enum("OWNER", "MEMBER", name="membership_role")


def _timestamps() -> tuple[sa.Column, sa.Column]:
    return (
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("google_sub", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("picture_url", sa.String(length=1024), nullable=True),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamps(),
        sa.UniqueConstraint("google_sub", name="uq_users_google_sub"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_google_sub", "users", ["google_sub"])
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "households",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"],
            ["users.id"],
            ondelete="RESTRICT",
            name="fk_households_created_by_user_id",
        ),
    )

    op.create_table(
        "household_memberships",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("household_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("partner_label", partner_label, nullable=False),
        sa.Column("role", membership_role, nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["household_id"],
            ["households.id"],
            ondelete="CASCADE",
            name="fk_memberships_household_id",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE", name="fk_memberships_user_id"
        ),
        sa.UniqueConstraint("household_id", "user_id", name="uq_membership_household_user"),
        sa.UniqueConstraint(
            "household_id", "partner_label", name="uq_membership_household_partner_label"
        ),
    )
    op.create_index("ix_memberships_household_id", "household_memberships", ["household_id"])
    op.create_index("ix_memberships_user_id", "household_memberships", ["user_id"])

    op.create_table(
        "household_invitations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("household_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=False),
        sa.Column("invited_email", sa.String(length=320), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("accepted_by_user_id", sa.Uuid(), nullable=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["household_id"],
            ["households.id"],
            ondelete="CASCADE",
            name="fk_invitations_household_id",
        ),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"],
            ["users.id"],
            ondelete="CASCADE",
            name="fk_invitations_created_by_user_id",
        ),
        sa.ForeignKeyConstraint(
            ["accepted_by_user_id"],
            ["users.id"],
            ondelete="SET NULL",
            name="fk_invitations_accepted_by_user_id",
        ),
        sa.UniqueConstraint("token_hash", name="uq_invitations_token_hash"),
    )
    op.create_index("ix_invitations_household_id", "household_invitations", ["household_id"])
    op.create_index("ix_invitations_token_hash", "household_invitations", ["token_hash"])

    op.create_table(
        "auth_sessions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("user_agent", sa.String(length=512), nullable=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE", name="fk_auth_sessions_user_id"
        ),
        sa.UniqueConstraint("token_hash", name="uq_auth_sessions_token_hash"),
    )
    op.create_index("ix_auth_sessions_user_id", "auth_sessions", ["user_id"])
    op.create_index("ix_auth_sessions_token_hash", "auth_sessions", ["token_hash"])


def downgrade() -> None:
    op.drop_table("auth_sessions")
    op.drop_table("household_invitations")
    op.drop_table("household_memberships")
    op.drop_table("households")
    op.drop_table("users")
    membership_role.drop(op.get_bind(), checkfirst=True)
    partner_label.drop(op.get_bind(), checkfirst=True)
