from pydantic import BaseModel
from uuid import UUID


class PetCreate(BaseModel):
    owner_id: UUID
    name: str
    weight: float | None = None
    age: int | None = None
    breed: str | None = None
    target_portion: float | None = None


class PetUpdate(BaseModel):
    name: str | None = None
    weight: float | None = None
    age: int | None = None
    breed: str | None = None
    target_portion: float | None = None
