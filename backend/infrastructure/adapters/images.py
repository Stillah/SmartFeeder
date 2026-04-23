import logging
import os
import datetime
from dataclasses import dataclass

import requests
from uuid import UUID
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from backend.services.interfaces.image import ImageInterface
from backend.infrastructure.db.image import ImageModel

# For classification
# SPECIFY !!!
THRESHOLD = 1.0
STORAGE_DIR = "storage/images"
EMBEDDINGS_URL = os.getenv("EMBEDDINGS_URL")

logger = logging.getLogger(__name__)


@dataclass
class ImageAdapter(ImageInterface):
    session: AsyncSession

    async def make_embedding(self, img: bytes) -> list[float] | None:
        if EMBEDDINGS_URL:
            files = {"file": ("image.jpg", img, "image/jpeg")}
            logger.info(
                "make_embedding: POST %s, image_bytes=%d",
                EMBEDDINGS_URL,
                len(img),
            )
            resp = requests.post(EMBEDDINGS_URL, files=files, timeout=120)
            logger.info(
                "make_embedding: response status=%s content_type=%s",
                resp.status_code,
                resp.headers.get("content-type"),
            )
            if not resp.ok:
                logger.error(
                    "make_embedding: non-OK response body (first 2k): %s",
                    resp.text[:2000],
                )
            try:
                data = resp.json()
            except ValueError:
                logger.error(
                    "make_embedding: response is not JSON, text (first 2k): %s",
                    resp.text[:2000],
                )
                raise
            if not isinstance(data, dict):
                logger.error(
                    "make_embedding: expected JSON object, got %s preview=%s",
                    type(data).__name__,
                    str(data)[:500],
                )
                raise ValueError(
                    f"Embeddings API returned {type(data).__name__}, expected object with 'embedding'"
                )
            if "embedding" not in data:
                logger.error(
                    "make_embedding: JSON has no 'embedding' key; keys=%s preview=%s",
                    list(data.keys()),
                    str(data)[:500],
                )
            return data["embedding"]

        raise Exception("Please specify EMBEDDINGS_URL in .env!")

    async def classify(
        self, embedding: list[float], user_id: UUID, k: int = 7
    ) -> UUID | None:
        stmt_with_dist = (
            select(
                ImageModel.pet_id,
                ImageModel.embedding.l2_distance(embedding).label("distance"),
            )
            .where(ImageModel.user_id == user_id)
            .order_by("distance")
            .limit(k)
        )

        result_dist = await self.session.execute(stmt_with_dist)
        rows = result_dist.all()

        if not rows:
            return None

        closest_dist = rows[0].distance

        if closest_dist > THRESHOLD:
            return None

        # Majority voting
        counts = {}
        for row in rows:
            counts[row.pet_id] = counts.get(row.pet_id, 0) + 1

        best_pet_id = max(counts, key=counts.get)
        return best_pet_id

    async def insert(
        self,
        embedding: list[float],
        pet_id: UUID,
        user_id: UUID,
        image_bytes: bytes | None = None,
        timestamp: datetime.datetime | None = None,
    ) -> UUID:
        image_path = None
        if image_bytes:
            os.makedirs(STORAGE_DIR, exist_ok=True)
            import uuid

            filename = f"{uuid.uuid4()}.jpg"
            image_path = os.path.join(STORAGE_DIR, filename)
            with open(image_path, "wb") as f:
                f.write(image_bytes)

        image = ImageModel(
            pet_id=pet_id, user_id=user_id, embedding=embedding, image_path=image_path
        )
        if timestamp is None:
            timestamp = datetime.datetime.now()
        image.timestamp = timestamp
        
        self.session.add(image)
        await self.session.commit()
        await self.session.refresh(image)
        return image.id

    async def get_latest_images(self, pet_id: UUID, limit: int = 5) -> list[str]:
        from sqlalchemy import func
        import base64

        stmt_max_ts = select(func.max(ImageModel.timestamp)).where(
            ImageModel.pet_id == pet_id, ImageModel.image_path.isnot(None)
        )
        result_max = await self.session.execute(stmt_max_ts)
        max_ts = result_max.scalar()

        if not max_ts:
            return []

        stmt = select(ImageModel.image_path).where(
            ImageModel.pet_id == pet_id,
            ImageModel.image_path.isnot(None),
            ImageModel.timestamp == max_ts,
        )

        result = await self.session.execute(stmt)
        paths = [row[0] for row in result.all()]

        images_base64 = []
        for path in paths:
            try:
                with open(path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode("utf-8")
                    images_base64.append(encoded)
            except Exception:
                pass
        return images_base64

    async def delete(self, id: UUID) -> None:
        stmt = delete(ImageModel).where(ImageModel.id == id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def delete_all(self) -> None:
        stmt = delete(ImageModel)
        await self.session.execute(stmt)
        await self.session.commit()
