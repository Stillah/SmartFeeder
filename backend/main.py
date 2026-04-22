import uvicorn
from fastapi import FastAPI
from backend.app.api.config import setup_routers

app = FastAPI(title="Smart Feeder API")

@app.get("/")
async def root():
    return {"message": "Welcome to Smart Feeder API. Docs: http://127.0.0.1:8000/docs"}

def main():
    setup_routers(app)
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == '__main__':
    main()
