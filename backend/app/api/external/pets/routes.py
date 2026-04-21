from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from pydantic import BaseModel
from backend.app.dependencies.adapters import get_pets_adapter
from backend.infrastructure.adapters.pet import PetsAdapter

router = APIRouter()

class PetCreate(BaseModel):
    owner_id: UUID
    name: str
    weight: float | None = None
    age: int | None = None
    breed: str | None = None
    target_portion: float | None = None

@router.post("/")
async def create_pet(pet: PetCreate, adapter: PetsAdapter = Depends(get_pets_adapter)):
    try:
        pet_id = await adapter.add(**pet.model_dump())
        return {"id": pet_id}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create pet: {str(e)}")

@router.get("/{pet_id}")
async def get_pet(pet_id: UUID, adapter: PetsAdapter = Depends(get_pets_adapter)):
    try:
        pet = await adapter.load(pet_id)
        if not pet:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pet not found")
        return pet
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to load pet: {str(e)}")
