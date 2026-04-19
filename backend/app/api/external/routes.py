from fastapi import APIRouter
from backend.app.api.external.pets.routes import router as pets_router
from backend.app.api.external.history.routes import router as history_router
from backend.app.api.external.status.routes import router as status_router
from backend.app.api.external.time_manager.routes import router as time_manager_router

router = APIRouter()

router.include_router(pets_router, prefix="/pets", tags=["External Pets"])
router.include_router(history_router, prefix="/history", tags=["External History"])
router.include_router(status_router, prefix="/status", tags=["External Status"])
router.include_router(time_manager_router, prefix="/schedules", tags=["External Schedules"])
