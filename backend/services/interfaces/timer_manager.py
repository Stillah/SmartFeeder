from typing import Protocol
from abc import abstractmethod
from uuid import UUID


class TimeManagmentInterface(Protocol):
    """Interface for working with time intervals for food disposal."""

    @abstractmethod
    async def add(self, user_id: UUID, start: int, end: int) -> None:
        """Add a time interval for disposing food for a user."""

    @abstractmethod
    async def load_all(self, user_id: UUID) -> list[tuple[int, int]]:
        """Load all time intervals for a user."""

    @abstractmethod
    async def update(
        self,
        user_id: UUID,
        old_start: int,
        old_end: int,
        new_start: int | None,
        new_end: int | None,
    ) -> None:
        """
        Edit interval parameters in the database.
        If new_start or new_end are None, then they remain unchanged.
        """

    @abstractmethod
    async def delete(self, user_id: UUID, start: int, end: int) -> None:
        """Delete a time interval for a user."""
