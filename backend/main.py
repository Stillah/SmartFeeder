from fastapi import FastAPI
from backend.app.api.external.routes import router as external_router
from backend.app.api.internal.routes import router as internal_router

app = FastAPI(title="Smart Feeder API")

app.include_router(external_router, prefix="/external")
app.include_router(internal_router, prefix="/internal")

@app.get("/")
async def root():
    return {"message": "Welcome to Smart Feeder API"}
