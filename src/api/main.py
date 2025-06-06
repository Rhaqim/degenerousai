from fastapi import FastAPI
from api.routers import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(router.router, prefix="/api/v1", tags=["v1"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://conexus.degenerousdao.com", "https://conexus-test.degenerousdao.com", "http://localhost:4321"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the API"}