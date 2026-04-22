import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from uuid import UUID
from backend.app.dependencies.adapters import get_image_adapter
from backend.infrastructure.adapters.images import ImageAdapter
from backend.infrastructure.exceptions.image import ClassificationError

router = APIRouter(prefix="/image", tags=["Internal Images"])

@router.post("/")
async def send_image(user_id: UUID, file: UploadFile, adapter: ImageAdapter = Depends(get_image_adapter)) -> UUID:
    try:
        img = await file.read()

        embedding = await adapter.make_embedding(img)

        label = await adapter.classify(embedding=embedding, user_id=user_id)
        if not label:
            raise ClassificationError()
        
        image_id = await adapter.insert(embedding=embedding, pet_id=label, user_id=user_id)
        # TODO: log that the cat came at this time
        
        return image_id
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to process the image: {str(e)}")
    
@router.delete("/{image_id}")
async def delete(image_id: UUID, adapter: ImageAdapter = Depends(get_image_adapter)) -> None:
    try:
        await adapter.delete(id=image_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete the image: {str(e)}")
    
@router.delete("/")
async def delete_all(adapter: ImageAdapter = Depends(get_image_adapter)) -> None:
    try:
        await adapter.delete_all()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete images: {str(e)}")
