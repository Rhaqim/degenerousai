from fastapi import FastAPI, Request, HTTPException
# Removed invalid import of Middleware
from starlette.types import ASGIApp

class APIKeyMiddleware:
    def __init__(self, app: ASGIApp, valid_api_keys: list[str]):
        self.app = app
        self.valid_api_keys = valid_api_keys

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope["headers"])
            api_key = headers.get(b"x-api-key", b"").decode()
            if not api_key or api_key not in self.valid_api_keys:
                raise HTTPException(status_code=401, detail="Invalid or missing API Key")
        await self.app(scope, receive, send)

# Example usage
app = FastAPI()

VALID_API_KEYS = ["your-api-key-1", "your-api-key-2"]

app.add_middleware(APIKeyMiddleware, valid_api_keys=VALID_API_KEYS)

@app.get("/")
async def root():
    return {"message": "Welcome to the API"}