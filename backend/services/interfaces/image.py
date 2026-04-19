import numpy as np
from abc import abstractmethod
from typing import Protocol
from uuid import UUID

class ImageInterface(Protocol):
    """Interface for working with camera images."""

    @abstractmethod
    async def make_embedding(self, img: bytes) -> list[float]:
        """Make an embedding from an image."""

    @abstractmethod
    async def classify(self, embedding: list[float], user_id: UUID, k: int = 7) -> UUID | None:
        """
        Classify an image embedding as a majority class in k nearest embeddings.
        Filtered by user_id.
        Returns pet_id or None if distance > threshold.
        """

    @abstractmethod
    async def insert(self, embedding: list[float], pet_id: UUID, user_id: UUID) -> UUID:
        """
        Insert an image into the database.
        Returns image_id.
        """

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        """Delete an image from the database."""
