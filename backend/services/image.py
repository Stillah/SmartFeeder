import datetime
import logging
from collections import Counter
from uuid import UUID

from fastapi import HTTPException, status

from backend.infrastructure.adapters.images import ImageAdapter
from backend.infrastructure.exceptions.image import ClassificationError

logger = logging.getLogger(__name__)


class ImageService:
    def __init__(self, image_adapter: ImageAdapter):
        self.adapter = image_adapter

    async def process_images(
        self,
        user_id: UUID,
        image_batch: list[bytes],
        timestamp: datetime.datetime | None = None,
    ) -> tuple[UUID, list[UUID]]:
        """Get pet_id of the pet in the images and the list of image_id's"""
        image_ids, embeddings = [], []
        labels = Counter()

        try:
            logger.info(
                "process_images: start user_id=%s batch_size=%s",
                user_id,
                len(image_batch),
            )
            for i, img in enumerate(image_batch):
                logger.info(
                    "process_images: image %d/%d — calling make_embedding",
                    i + 1,
                    len(image_batch),
                )
                embedding = await self.adapter.make_embedding(img)
                logger.info(
                    "process_images: image %d/%d — embedding dim=%s",
                    i + 1,
                    len(image_batch),
                    len(embedding) if embedding else None,
                )
                logger.info(
                    "process_images: image %d/%d — calling classify",
                    i + 1,
                    len(image_batch),
                )
                label = await self.adapter.classify(
                    embedding=embedding, user_id=user_id
                )
                embeddings.append(embedding)

                if not label:
                    logger.warning(
                        "process_images: image %d/%d — classify returned no label",
                        i + 1,
                        len(image_batch),
                    )
                    raise ClassificationError("Could not classify image")

                labels[label] += 1

            most_common_label = labels.most_common(1)[0][0]
            logger.info(
                "process_images: majority pet_id=%s labels=%s",
                most_common_label,
                dict(labels),
            )
            for embedding, img_bytes in zip(embeddings, image_batch, strict=True):
                image_id = await self.adapter.insert(
                    embedding=embedding,
                    pet_id=most_common_label,
                    user_id=user_id,
                    image_bytes=img_bytes,
                    timestamp=timestamp,
                )
                image_ids.append(image_id)

            logger.info("process_images: done image_ids=%s", image_ids)
            return (most_common_label, image_ids)

        except Exception as e:
            logger.exception(
                "process_images: failed user_id=%s error=%s",
                user_id,
                e,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process the images: {str(e)}",
            )
