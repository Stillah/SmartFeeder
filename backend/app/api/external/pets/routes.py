from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List
from backend.app.dependencies.adapters import get_pets_adapter
from backend.infrastructure.adapters.pet import PetsAdapter
from backend.schemas.pets import PetCreate, PetUpdate, PetResponse

router = APIRouter(prefix="/pets", tags=["External Pets"])


@router.post("/")
async def create_pet(pet: PetCreate, adapter: PetsAdapter = Depends(get_pets_adapter)):
    try:
        pet_id = await adapter.add(**pet.model_dump())
        return {"id": pet_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create pet: {str(e)}",
        )


@router.get("/{pet_id}")
async def get_pet(pet_id: UUID, adapter: PetsAdapter = Depends(get_pets_adapter)):
    try:
        pet = await adapter.load(pet_id)
        if not pet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Pet not found"
            )
        return pet
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load pet: {str(e)}",
        )


@router.put("/{pet_id}")
async def update_pet(
    pet_id: UUID,
    pet_update: PetUpdate,
    adapter: PetsAdapter = Depends(get_pets_adapter),
):
    try:
        await adapter.update(pet_id, **pet_update.model_dump(exclude_unset=True))
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update pet: {str(e)}",
        )


@router.delete("/{pet_id}")
async def delete_pet(pet_id: UUID, adapter: PetsAdapter = Depends(get_pets_adapter)):
    try:
        await adapter.delete(pet_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete pet: {str(e)}",
        )


@router.get("/user/{user_id}", response_model=List[PetResponse])
async def get_user_pets(
    user_id: UUID, adapter: PetsAdapter = Depends(get_pets_adapter)
):
    try:
        pets = await adapter.get_by_owner_id(user_id)
        return [PetResponse.model_validate(pet) for pet in pets]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch pets: {str(e)}",
        )
