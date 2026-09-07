import uuid

from pydantic import BaseModel, ConfigDict

from app.schemas.household import HouseholdOut


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    name: str
    picture_url: str | None = None


class MeOut(BaseModel):
    user: UserOut
    household: HouseholdOut | None = None
