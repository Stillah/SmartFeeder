import numpy as np
import os
from dataclasses import dataclass
from uuid import UUID
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from backend.services.interfaces.image import ImageInterface
from backend.infrastructure.db.image import ImageModel

# For classification
# SPECIFY !!!
THRESHOLD = 1.0
STORAGE_DIR = "storage/images"

@dataclass
class ImageAdapter(ImageInterface):
    session: AsyncSession

    async def make_embedding(self, img: bytes) -> list[float]:
        pass

    async def classify(self, embedding: list[float], user_id: UUID, k: int = 7) -> UUID | None:
        stmt_with_dist = select(
            ImageModel.pet_id,
            ImageModel.embedding.l2_distance(embedding).label('distance')
        ).where(
            ImageModel.user_id == user_id
        ).order_by('distance').limit(k)
        
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

    async def insert(self, embedding: list[float], pet_id: UUID, user_id: UUID, image_bytes: bytes | None = None) -> UUID:
        image_path = None
        if image_bytes:
            os.makedirs(STORAGE_DIR, exist_ok=True)
            import uuid
            filename = f"{uuid.uuid4()}.jpg"
            image_path = os.path.join(STORAGE_DIR, filename)
            with open(image_path, "wb") as f:
                f.write(image_bytes)

        image = ImageModel(pet_id=pet_id, user_id=user_id, embedding=embedding, image_path=image_path)
        self.session.add(image)
        await self.session.commit()
        await self.session.refresh(image)
        return image.id

    async def get_latest_images(self, pet_id: UUID, limit: int = 5) -> list[str]:
        stmt = select(ImageModel.image_path).where(
            ImageModel.pet_id == pet_id,
            ImageModel.image_path.isnot(None)
        ).order_by(ImageModel.timestamp.desc()).limit(limit)
        
        result = await self.session.execute(stmt)
        return [row[0] for row in result.all()]

    async def delete(self, id: UUID) -> None:
        stmt = delete(ImageModel).where(ImageModel.id == id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def delete_all(self) -> None:
        stmt = delete(ImageModel)
        await self.session.execute(stmt)
        await self.session.commit()
