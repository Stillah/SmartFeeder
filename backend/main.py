import uvicorn
from fastapi import FastAPI
from backend.app.api.external.routes import router as external_router
from backend.app.api.internal.routes import router as internal_router

app = FastAPI(title="Smart Feeder API")



@app.get("/")
async def root():
    return {"message": "Welcome to Smart Feeder API. Docs: http://127.0.0.1:8000/docs"}

def main():
    app.include_router(external_router, prefix="/external")
    app.include_router(internal_router, prefix="/internal")
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == '__main__':
    main()
