from fastapi import FastAPI
from api.routers import router

app = FastAPI()

app.include_router(router.router, prefix="/api/v1", tags=["v1"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the API"}