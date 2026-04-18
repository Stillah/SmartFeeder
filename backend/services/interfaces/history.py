from typing import Protocol
from abc import abstractmethod

class HistoryInterface(Protocol):
    """Interface for getting info about pets."""

    @abstractmethod
    def get_food_consumption_mean(self, pet_id: int) -> float:
        """Get an average food consumption for a specific pet."""

    @abstractmethod
    def get_food_consumption_std(self, pet_id: int) -> float:
        """Get a standard deviation for food consumption of a specific pet."""

    @abstractmethod
    def get_average_eating_times(self, pet_id: int) -> list[float]:
        """Get average day times for when pets eat (e.g. for breakfast and dinner)."""