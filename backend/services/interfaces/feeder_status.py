from typing import Protocol
from abc import abstractmethod
from time import struct_time


class FeederStatusInterface(Protocol):
    """Interface for getting info about the misc."""

    @abstractmethod
    def get_last_connection_time(self) -> struct_time:
        """Get the last timestamp when the hardware successfully connected to the server."""

    @abstractmethod
    def get_current_food_weight(self) -> float:
        """Get current food weight in the bowl."""

    def update_feeder_weight(self, new_weight: float) -> None:
        """Update the weight in the bowl."""



