from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from uuid import UUID
from backend.app.dependencies.adapters import get_image_adapter, get_history_adapter
from backend.infrastructure.adapters.images import ImageAdapter
from backend.infrastructure.adapters.history import HistoryAdapter
from backend.services.image import ImageService

router = APIRouter(prefix="/logs", tags=["Internal Images"])


@router.post("/")
async def create_log(
    user_id: UUID,
    food_weight: float,
    files_batch: list[UploadFile],
    image_adapter: ImageAdapter = Depends(get_image_adapter),
    history_adapter: HistoryAdapter = Depends(get_history_adapter),
) -> list[UUID]:
    try:
        images = [await file.read() for file in files_batch]
        service = ImageService(image_adapter)
        pet_id, image_ids = await service.process_images(user_id, images)

        # Add your extra functionality here
        await history_adapter.add_feeding_log(pet_id=pet_id, amount_eaten=food_weight)
        return image_ids

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create log: {str(e)}")
