from typing import Protocol
from abc import abstractmethod
from datetime import datetime


class FeederStatusInterface(Protocol):
    """Interface for getting info about the misc."""

    @abstractmethod
    async def get_last_connection_time(self) -> datetime:
        """Get the last timestamp when the hardware successfully connected to the server."""

    @abstractmethod
    async def get_current_food_weight(self) -> float:
        """Get current food weight in the bowl."""

    @abstractmethod
    async def update_feeder_weight(self, new_weight: float) -> None:
        """Update the weight in the bowl."""

    @abstractmethod
    async def update_connection_time(self) -> None:
        """Update the last connection time."""
