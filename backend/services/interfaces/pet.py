from typing import Protocol
from abc import abstractmethod
from uuid import UUID

from backend.infrastructure.db.pet import PetModel

class PetsInterface(Protocol):
    """Interface for working with pets."""

    @abstractmethod
    def add(self, name: str, weight: float | None, age: int | None, breed: str | None) -> UUID:
        """Add a pet to the database."""

    @abstractmethod
    def load(self, id: UUID) -> PetModel:
        """Load a pet from the database by id."""

    @abstractmethod
    def update(self, **kwargs) -> None:
        """Edit pet parameters in the database."""

    @abstractmethod
    def delete(self, id: int) -> None:
        """Delete a pet from the database."""