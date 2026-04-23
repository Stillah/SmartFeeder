import datetime
from abc import abstractmethod
from typing import Protocol
from uuid import UUID


class ImageInterface(Protocol):
    """Interface for working with camera images."""

    @abstractmethod
    async def make_embedding(self, img: bytes) -> list[float] | None:
        """Make an embedding from an image."""

    @abstractmethod
    async def classify(
        self, embedding: list[float], user_id: UUID, k: int = 7
    ) -> UUID:
        """
        Classify an image embedding as a majority class among k nearest embeddings
        (cosine distance), filtered by user_id. If there is no reference data or
        the nearest neighbor is too far, creates a new pet and returns its id.
        """

    @abstractmethod
    async def insert(
        self,
        embedding: list[float],
        pet_id: UUID,
        user_id: UUID,
        image_bytes: bytes | None = None,
        timestamp: "datetime.datetime | None" = None,
    ) -> UUID:
        """
        Insert an image into the database and optionally save it locally.
        Returns image_id.
        """

    @abstractmethod
    async def get_latest_images(self, pet_id: UUID, limit: int = 5) -> list[str]:
        """
        Get the latest image paths for a specific pet.
        """

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        """Delete an image from the database."""
