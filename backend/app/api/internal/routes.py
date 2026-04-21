from fastapi import APIRouter
from backend.app.api.internal.images.routes import router as image_router

router = APIRouter()

router.include_router(image_router, prefix="/image", tags=["Internal Images"])
