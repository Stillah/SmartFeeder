from typing import Protocol
from abc import abstractmethod
from uuid import UUID

from backend.infrastructure.db.pet import PetModel


class PetsInterface(Protocol):
    """Interface for working with pets."""

    @abstractmethod
    async def add(
        self,
        owner_id: UUID,
        name: str = "Unnamed cat",
        weight: float | None = None,
        age: int | None = None,
        breed: str | None = None,
        target_portion: float | None = None,
    ) -> UUID:
        """Add a pet to the database."""

    @abstractmethod
    async def load(self, id: UUID) -> PetModel:
        """Load a pet from the database by id."""

    @abstractmethod
    async def update(self, id: UUID, **kwargs) -> None:
        """Edit pet parameters in the database."""

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        """Delete a pet from the database."""
