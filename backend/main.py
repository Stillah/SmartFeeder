import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.app.api.config import setup_routers
from backend.infrastructure.db.init_db import init_db
from backend.infrastructure.db.seed import seed_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await seed_db()
    yield
    pass

app = FastAPI(title="Smart Feeder API", lifespan=lifespan)
setup_routers(app)

@app.get("/")
async def root():
    return {"message": "Welcome to Smart Feeder API. Docs: http://127.0.0.1:8000/docs"}

def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == '__main__':
    main()
