import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from uuid import UUID
from backend.app.dependencies.adapters import get_image_adapter
from backend.infrastructure.adapters.images import ImageAdapter
from backend.infrastructure.exceptions.image import ClassificationError
from collections import Counter


class ImageService:
    def __init__(self, image_adapter: ImageAdapter):
        self.adapter = image_adapter

    async def process_images(
        self,
        user_id: UUID,
        image_batch: list[bytes],
    ) -> tuple[UUID, list[UUID]]:
        """Get pet_id of the pet in the images and the list of image_id's"""
        image_ids, embeddings = [], []
        labels = Counter()

        try:
            for img in image_batch:
                embedding = await self.adapter.make_embedding(img)
                label = await self.adapter.classify(
                    embedding=embedding, user_id=user_id
                )
                embeddings.append(embedding)

                if not label:
                    raise ClassificationError("Could not classify image")

                labels[label] += 1

            most_common_label = labels.most_common(1)[0][0]
            for embedding in embeddings:
                image_id = await self.adapter.insert(
                    embedding=embedding, pet_id=most_common_label, user_id=user_id
                )
                image_ids.append(image_id)

            return (most_common_label, image_ids)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process the images: {str(e)}",
            )
