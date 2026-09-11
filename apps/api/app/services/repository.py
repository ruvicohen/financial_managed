"""Household-scoped repository base.

Every later phase's data (accounts, transactions, documents, ...) is owned by a
household. This base makes the scope impossible to forget: build queries with
:meth:`scoped` and fetch single rows with :meth:`get_or_404`, both of which pin
``household_id`` to the caller's household. Rows belonging to another household
are indistinguishable from missing ones (404), never leaked.
"""

import uuid
from typing import Any, TypeVar

from fastapi import HTTPException, status
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.db.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class HouseholdScopedRepository:
    def __init__(self, db: Session, household_id: uuid.UUID) -> None:
        self.db = db
        self.household_id = household_id

    def scoped(self, model: type[ModelT]) -> Select[tuple[ModelT]]:
        column = model.__table__.c["household_id"]
        return select(model).where(column == self.household_id)

    def get_or_404(self, model: type[ModelT], obj_id: Any, *, detail: str = "Not found") -> ModelT:
        obj = self.db.get(model, obj_id)
        if obj is None or getattr(obj, "household_id", None) != self.household_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
        return obj
