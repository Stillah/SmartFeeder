from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from uuid import UUID
from backend.app.dependencies.adapters import get_image_adapter
from backend.infrastructure.adapters.images import ImageAdapter

router = APIRouter(prefix="/images", tags=["External Images"])


@router.get("/{pet_id}/latest", response_model=List[str])
async def get_latest_images(
    pet_id: UUID,
    limit: int = Query(5, ge=1, le=50),
    adapter: ImageAdapter = Depends(get_image_adapter),
):
    try:
        return await adapter.get_latest_images(pet_id, limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get latest images: {str(e)}",
        )
