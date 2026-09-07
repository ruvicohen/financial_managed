"""Phase 1 acceptance: one household cannot reach another's data."""

from collections.abc import Callable

import pytest
from app.models import HouseholdMembership, User
from app.services.households import HouseholdService
from app.services.repository import HouseholdScopedRepository
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

MakeUser = Callable[..., User]
AuthClient = Callable[[User], TestClient]


def test_current_household_endpoint_is_scoped_to_the_caller(
    make_user: MakeUser, auth_client: AuthClient
) -> None:
    user_a, user_b = make_user(name="A"), make_user(name="B")

    h1 = auth_client(user_a).post("/api/v1/households", json={"name": "H1"}).json()
    h2 = auth_client(user_b).post("/api/v1/households", json={"name": "H2"}).json()
    assert h1["id"] != h2["id"]

    seen_by_a = auth_client(user_a).get("/api/v1/households/current").json()
    assert seen_by_a["id"] == h1["id"]
    assert [m["name"] for m in seen_by_a["members"]] == ["A"]

    seen_by_b = auth_client(user_b).get("/api/v1/households/current").json()
    assert seen_by_b["id"] == h2["id"]
    assert [m["name"] for m in seen_by_b["members"]] == ["B"]


def test_user_without_household_gets_403_not_someone_elses(
    make_user: MakeUser, auth_client: AuthClient
) -> None:
    owner, outsider = make_user(), make_user()
    auth_client(owner).post("/api/v1/households", json={"name": "H1"})

    resp = auth_client(outsider).get("/api/v1/households/current")
    assert resp.status_code == 403


def test_scoped_repository_hides_other_households_rows(make_user: MakeUser, db: Session) -> None:
    user_a, user_b = make_user(), make_user()
    svc = HouseholdService(db)
    h1 = svc.provision_for_user(user_a, "H1")
    h2 = svc.provision_for_user(user_b, "H2")

    h2_membership = (
        db.query(HouseholdMembership).filter(HouseholdMembership.household_id == h2.id).one()
    )

    repo = HouseholdScopedRepository(db, h1.id)

    # cross-household fetch is indistinguishable from missing
    with pytest.raises(HTTPException) as exc:
        repo.get_or_404(HouseholdMembership, h2_membership.id)
    assert exc.value.status_code == 404

    scoped_ids = {
        row.household_id for row in db.execute(repo.scoped(HouseholdMembership)).scalars()
    }
    assert scoped_ids == {h1.id}


def test_cannot_join_another_household_when_already_a_member(
    make_user: MakeUser, auth_client: AuthClient, db: Session
) -> None:
    user_a, user_b = make_user(), make_user()

    client_b = auth_client(user_b)
    client_b.post("/api/v1/households", json={"name": "H2"})

    client_a = auth_client(user_a)
    client_a.post("/api/v1/households", json={"name": "H1"})
    invite_token = client_a.post("/api/v1/households/current/invitations").json()["token"]

    # user_b already owns H2 -> accepting H1's invite must fail and not leak H1
    resp = client_b.post("/api/v1/households/invitations/accept", json={"token": invite_token})
    assert resp.status_code == 409
    still_h2 = client_b.get("/api/v1/households/current").json()
    assert still_h2["name"] == "H2"
    assert len(still_h2["members"]) == 1
