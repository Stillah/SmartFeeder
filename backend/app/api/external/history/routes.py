from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from uuid import UUID
from backend.app.dependencies.adapters import get_history_adapter
from backend.infrastructure.adapters.history import HistoryAdapter
from backend.schemas.history import FeedingLogResponse, AnalysisResponse

router = APIRouter(prefix="/history", tags=["External History"])

@router.get("/{pet_id}/recent", response_model=List[FeedingLogResponse])
async def get_recent_feedings(
    pet_id: UUID, 
    limit: int = Query(10, ge=1, le=100),
    adapter: HistoryAdapter = Depends(get_history_adapter)
):
    try:
        return await adapter.get_recent_feedings(pet_id, limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get recent feedings: {str(e)}")

@router.get("/{pet_id}/analysis", response_model=AnalysisResponse)
async def get_pet_analysis(pet_id: UUID, adapter: HistoryAdapter = Depends(get_history_adapter)):
    try:
        return await adapter.get_analysis(pet_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get pet analysis: {str(e)}")
