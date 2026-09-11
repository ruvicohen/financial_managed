import hashlib
from collections.abc import Callable
from datetime import UTC, datetime, timedelta

import pytest
from app.auth.dependencies import HouseholdContext
from app.models import (
    HouseholdInvitation,
    HouseholdMembership,
    MembershipRole,
    PartnerLabel,
    User,
)
from app.services.households import HouseholdService
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

MakeUser = Callable[..., User]
AuthClient = Callable[[User], TestClient]


def _hash(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


def test_create_household_makes_owner_partner_a(
    make_user: MakeUser, auth_client: AuthClient
) -> None:
    client = auth_client(make_user())
    resp = client.post("/api/v1/households", json={"name": "Cohen"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "Cohen"
    assert len(body["members"]) == 1
    assert body["members"][0]["partner_label"] == PartnerLabel.PARTNER_A
    assert body["members"][0]["role"] == MembershipRole.OWNER


def test_second_create_by_same_user_conflicts(make_user: MakeUser, auth_client: AuthClient) -> None:
    client = auth_client(make_user())
    assert client.post("/api/v1/households", json={"name": "One"}).status_code == 201
    assert client.post("/api/v1/households", json={"name": "Two"}).status_code == 409


def test_invite_and_accept_flow(make_user: MakeUser, auth_client: AuthClient) -> None:
    user_a, user_b = make_user(), make_user()

    client = auth_client(user_a)
    client.post("/api/v1/households", json={"name": "Shared"})
    invite = client.post("/api/v1/households/current/invitations")
    assert invite.status_code == 201
    token = invite.json()["token"]
    assert invite.json()["invite_url"].endswith(f"/join?token={token}")

    # owner cannot create a second pending invite
    assert client.post("/api/v1/households/current/invitations").status_code == 409

    client_b = auth_client(user_b)
    accepted = client_b.post("/api/v1/households/invitations/accept", json={"token": token})
    assert accepted.status_code == 201
    members = {m["partner_label"]: m for m in accepted.json()["members"]}
    assert members[PartnerLabel.PARTNER_B]["role"] == MembershipRole.MEMBER
    assert len(members) == 2

    # token is single-use
    user_c = make_user()
    reuse = auth_client(user_c).post("/api/v1/households/invitations/accept", json={"token": token})
    assert reuse.status_code == 400


def test_expired_invitation_is_rejected(
    make_user: MakeUser, auth_client: AuthClient, db: Session
) -> None:
    user_a, user_b = make_user(), make_user()
    client = auth_client(user_a)
    client.post("/api/v1/households", json={"name": "Shared"})
    household_id = client.get("/api/v1/households/current").json()["id"]

    db.add(
        HouseholdInvitation(
            household_id=household_id,
            token_hash=_hash("expired-token"),
            created_by_user_id=user_a.id,
            expires_at=datetime.now(UTC) - timedelta(hours=1),
        )
    )
    db.flush()

    resp = auth_client(user_b).post(
        "/api/v1/households/invitations/accept", json={"token": "expired-token"}
    )
    assert resp.status_code == 400


def test_create_invitation_replaces_expired_pending_invitation(
    make_user: MakeUser, auth_client: AuthClient, db: Session
) -> None:
    """Regression: uq_invitations_active_per_household allows only one
    accepted_at-IS-NULL row per household, so create_invitation must clear an
    expired-but-never-accepted invite before inserting a new one."""
    user_a = make_user()
    client = auth_client(user_a)
    client.post("/api/v1/households", json={"name": "Shared"})
    household_id = client.get("/api/v1/households/current").json()["id"]

    db.add(
        HouseholdInvitation(
            household_id=household_id,
            token_hash=_hash("expired-token"),
            created_by_user_id=user_a.id,
            expires_at=datetime.now(UTC) - timedelta(hours=1),
        )
    )
    db.flush()

    resp = client.post("/api/v1/households/current/invitations")
    assert resp.status_code == 201


def test_household_capped_at_two_members(make_user: MakeUser, db: Session) -> None:
    user_a, user_b, user_c = make_user(), make_user(), make_user()
    svc = HouseholdService(db)
    household = svc.provision_for_user(user_a, "Shared")
    db.add(
        HouseholdMembership(
            household_id=household.id,
            user_id=user_b.id,
            partner_label=PartnerLabel.PARTNER_B,
            role=MembershipRole.MEMBER,
        )
    )
    db.add(
        HouseholdInvitation(
            household_id=household.id,
            token_hash=_hash("late-token"),
            created_by_user_id=user_a.id,
            expires_at=datetime.now(UTC) + timedelta(days=1),
        )
    )
    db.flush()

    with pytest.raises(HTTPException) as exc:
        svc.accept_invitation(user_c, "late-token")
    assert exc.value.status_code == 409


def test_non_owner_cannot_invite(make_user: MakeUser, db: Session) -> None:
    user_a, user_b = make_user(), make_user()
    svc = HouseholdService(db)
    household = svc.provision_for_user(user_a, "Shared")
    member_b = HouseholdMembership(
        household_id=household.id,
        user_id=user_b.id,
        partner_label=PartnerLabel.PARTNER_B,
        role=MembershipRole.MEMBER,
    )
    db.add(member_b)
    db.flush()

    ctx = HouseholdContext(household_id=household.id, user=user_b, membership=member_b)
    with pytest.raises(HTTPException) as exc:
        svc.create_invitation(ctx)
    assert exc.value.status_code == 403
