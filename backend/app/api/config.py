from fastapi import FastAPI
from backend.app.api.external.pets.routes import router as pets_router
from backend.app.api.external.history.routes import router as history_router
from backend.app.api.external.status.routes import router as status_router
from backend.app.api.external.time_manager.routes import router as time_manager_router
from backend.app.api.external.images.routes import router as external_images_router
from backend.app.api.internal.images.routes import router as image_router
from backend.app.api.internal.logs.routes import router as logs_router


def setup_routers(app: FastAPI) -> None:
    app.include_router(pets_router)
    app.include_router(history_router)
    app.include_router(status_router)
    app.include_router(time_manager_router)
    app.include_router(external_images_router)
    app.include_router(image_router)
    app.include_router(logs_router)
