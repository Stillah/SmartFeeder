from fastapi import APIRouter, Depends, HTTPException, status
from backend.app.dependencies.adapters import get_feeder_status_adapter
from backend.infrastructure.adapters.feeder_status import FeederStatusAdapter

router = APIRouter(prefix="/status", tags=["External Status"])


@router.get("/")
async def get_feeder_status(
    adapter: FeederStatusAdapter = Depends(get_feeder_status_adapter),
):
    try:
        weight = await adapter.get_current_food_weight()
        last_conn = await adapter.get_last_connection_time()
        return {"current_food_weight": weight, "last_connection": last_conn}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get feeder status: {str(e)}",
        )
