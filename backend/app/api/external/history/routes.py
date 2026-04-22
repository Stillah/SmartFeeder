from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from backend.app.dependencies.adapters import get_history_adapter
from backend.infrastructure.adapters.history import HistoryAdapter

router = APIRouter(prefix="/history", tags=["External History"])


@router.get("/{pet_id}")
async def get_pet_history(
    pet_id: UUID, adapter: HistoryAdapter = Depends(get_history_adapter)
):
    try:
        mean = await adapter.get_food_consumption_mean(pet_id)
        std = await adapter.get_food_consumption_std(pet_id)
        times = await adapter.get_average_eating_times(pet_id)
        return {"mean": mean, "std": std, "average_eating_times": times}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pet history: {str(e)}",
        )
