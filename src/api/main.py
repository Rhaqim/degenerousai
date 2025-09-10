from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import openai, processor, test

app = FastAPI()

app.include_router(openai.router, prefix="/api/v1", tags=["v1"])
app.include_router(processor.router, prefix="/api/v1", tags=["v1"])
app.include_router(test.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://conexus.degenerousdao.com",
        "https://conexus-test.degenerousdao.com",
        "http://localhost:4321",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Welcome to the API"}
