import numpy as np
from abc import abstractmethod
from typing import Protocol
from uuid import UUID

class ImageInterface(Protocol):
    """Interface for working with camera images."""

    @abstractmethod
    def make_embedding(self, img) -> np.ndarray:
        """Make an embedding from an image."""

    @abstractmethod
    def classify(self, embedding: np.ndarray, k: int = 7) -> int:
        """
        Classify an image embedding as a majority class in k nearest embeddings.
        Returns pet_id.
        """

    @abstractmethod
    def insert(self, embedding: np.ndarray, pet_id: int) -> UUID:
        """
        Insert an image into the database.
        Returns image_id.
        """

    @abstractmethod
    def delete(self, id) -> None:
        """Delete an image from the database."""

    