from typing import Protocol, List
from abc import abstractmethod
from uuid import UUID
from backend.schemas.history import FeedingLogResponse, AnalysisResponse


class HistoryInterface(Protocol):
    """Interface for getting info about pets."""

    @abstractmethod
    async def get_food_consumption_mean(self, pet_id: UUID) -> float:
        """Get an average food consumption for a specific pet."""

    @abstractmethod
    async def get_food_consumption_std(self, pet_id: UUID) -> float:
        """Get a standard deviation for food consumption of a specific pet."""

    @abstractmethod
    async def get_average_eating_times(self, pet_id: UUID) -> list[float]:
        """Get average day times for when pets eat (e.g. for breakfast and dinner)."""

    @abstractmethod
    async def add_feeding_log(self, pet_id: UUID, amount_eaten: float) -> None:
        """Add a feeding log entry."""

    @abstractmethod
    async def get_recent_feedings(
        self, pet_id: UUID, limit: int = 10
    ) -> List[FeedingLogResponse]:
        """Get recent feeding logs for a specific pet."""

    @abstractmethod
    async def get_analysis(self, pet_id: UUID) -> AnalysisResponse:
        """Get combined analysis for a specific pet."""
