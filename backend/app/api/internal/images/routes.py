import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from uuid import UUID
from backend.app.dependencies.adapters import get_image_adapter
from backend.infrastructure.adapters.images import ImageAdapter
from backend.infrastructure.exceptions.image import ClassificationError
from collections import Counter
from backend.services.image import ImageService

router = APIRouter(prefix="/image", tags=["Internal Images"])


@router.post("/")
async def send_image(
    user_id: UUID,
    files: list[UploadFile],
    adapter: ImageAdapter = Depends(get_image_adapter),
) -> tuple[UUID, list[UUID]]:
    """Get pet_id of the pet in the images and the list of image_id's"""
    try:
        images = [await file.read() for file in files]
        service = ImageService(adapter)
        return await service.process_images(user_id, images)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to process images: {str(e)}"
        )


@router.delete("/{image_id}")
async def delete(
    image_id: UUID, adapter: ImageAdapter = Depends(get_image_adapter)
) -> None:
    try:
        await adapter.delete(id=image_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete the image: {str(e)}",
        )


@router.delete("/")
async def delete_all(adapter: ImageAdapter = Depends(get_image_adapter)) -> None:
    try:
        await adapter.delete_all()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete images: {str(e)}",
        )
