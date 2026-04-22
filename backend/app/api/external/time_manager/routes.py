from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from backend.app.dependencies.adapters import get_time_manager_adapter
from backend.infrastructure.adapters.time_manager import TimeManagerAdapter
from backend.schemas.schedules import ScheduleCreate

router = APIRouter(prefix="/schedules", tags=["External Schedules"])

@router.post("/")
async def add_schedule(schedule: ScheduleCreate, adapter: TimeManagerAdapter = Depends(get_time_manager_adapter)):
    try:
        await adapter.add(schedule.user_id, schedule.start_time, schedule.end_time)
        return {"status": "success"}
    except Exception as e:
        # Add logging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add schedule: {str(e)}"
        )

@router.get("/{user_id}")
async def get_schedules(user_id: UUID, adapter: TimeManagerAdapter = Depends(get_time_manager_adapter)):
    try:
        schedules = await adapter.load_all(user_id)
        return {"schedules": schedules}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load schedules: {str(e)}"
        )
