from typing import Optional

from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from database.api_keys import APIKeyManager

router = APIRouter()
api_key_manager = APIKeyManager()


#
# API Key Model
class APIKey(BaseModel):
    user_id: UUID
    api_key: str
    # Optional: Add any other fields you want to include in the API key model
    # For example, you might want to include a timestamp for when the key was created
    # created_at: datetime = Field(default_factory=datetime.utcnow)
    # Optional: Add any other fields you want to include in the API key model


class APIKeyResponse(BaseModel):
    api_key: str
    message: Optional[str] = None
    error: Optional[str] = None
    # Optional: Add any other fields you want to include in the API key response model


class APIKeyListResponse(BaseModel):
    api_keys: list[APIKeyResponse]
    message: Optional[str] = None
    error: Optional[str] = None
    # Optional: Add any other fields you want to include in the API key list response model


class APIKeyErrorResponse(BaseModel):
    error: str
    message: Optional[str] = None
    # Optional: Add any other fields you want to include in the API key error response model


class APIKeySuccessResponse(BaseModel):
    message: str
    # Optional: Add any other fields you want to include in the API key success response model


class APIKeyDeleteResponse(BaseModel):
    message: str
    # Optional: Add any other fields you want to include in the API key delete response model


class APIKeyUpdateResponse(BaseModel):
    message: str
    # Optional: Add any other fields you want to include in the API key update response model


class APIKeyCreateResponse(BaseModel):
    api_key: str
    message: Optional[str] = None
    error: Optional[str] = None
    # Optional: Add any other fields you want to include in the API key create response model


class APIKeyCreateRequest(BaseModel):
    user_id: UUID
    api_key: str = Field(..., min_length=32, max_length=128)
    # Optional: Add any other fields you want to include in the API key create request model
    # For example, you might want to include a timestamp for when the key was created
    # created_at: datetime = Field(default_factory=datetime.utcnow)
    # Optional: Add any other fields you want to include in the API key create request model


@router.post("/api_keys/create", response_model=APIKeyCreateResponse)
async def create(request: APIKeyCreateRequest):
    """
    Endpoint to create a new API key.
    """
    try:
        api_key_manager.create_api_key(request.user_id, request.api_key)
        return JSONResponse(
            content={
                "api_key": request.api_key,
                "message": "API key created successfully",
            },
            status_code=201,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api_keys/{user_id}", response_model=APIKeyResponse)
async def read(user_id: UUID):
    """
    Endpoint to read an API key for a specific user.
    """
    try:
        api_key = api_key_manager.read_api_key(user_id)
        if api_key:
            return JSONResponse(
                content={
                    "api_key": api_key,
                    "message": "API key retrieved successfully",
                },
                status_code=200,
            )
        else:
            raise HTTPException(status_code=404, detail="API key not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/api_keys/update", response_model=APIKeyUpdateResponse)
async def update(request: APIKeyCreateRequest):
    """
    Endpoint to update an existing API key.
    """
    try:
        api_key_manager.update_api_key(request.user_id, request.api_key)
        return JSONResponse(
            content={"message": "API key updated successfully"},
            status_code=200,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api_keys/delete/{user_id}", response_model=APIKeyDeleteResponse)
async def delete(user_id: UUID):
    """
    Endpoint to delete an API key for a specific user.
    """
    try:
        api_key_manager.delete_api_key(user_id)
        return JSONResponse(
            content={"message": "API key deleted successfully"},
            status_code=200,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api_keys", response_model=APIKeyListResponse)
async def list_api_keys():
    """
    Endpoint to list all API keys.
    """
    try:
        api_keys = api_key_manager.db.fetch_all("SELECT * FROM api_keys")
        return JSONResponse(
            content={
                "api_keys": api_keys,
                "message": "API keys retrieved successfully",
            },
            status_code=200,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api_keys/{user_id}/delete", response_model=APIKeyDeleteResponse)
async def delete_api_key(user_id: UUID):
    """
    Endpoint to delete an API key for a specific user.
    """
    try:
        api_key_manager.delete_api_key(user_id)
        return JSONResponse(
            content={"message": "API key deleted successfully"},
            status_code=200,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api_keys/{user_id}/update", response_model=APIKeyUpdateResponse)
async def update_api_key(user_id: UUID, new_api_key: str):
    """
    Endpoint to update an existing API key.
    """
    try:
        api_key_manager.update_api_key(user_id, new_api_key)
        return JSONResponse(
            content={"message": "API key updated successfully"},
            status_code=200,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api_keys/{user_id}/create", response_model=APIKeyCreateResponse)
async def create_api_key(user_id: UUID, api_key: str):
    """
    Endpoint to create a new API key.
    """
    try:
        api_key_manager.create_api_key(user_id, api_key)
        return JSONResponse(
            content={"api_key": api_key, "message": "API key created successfully"},
            status_code=201,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api_keys/{user_id}/read", response_model=APIKeyResponse)
async def read_api_key(user_id: UUID):
    """
    Endpoint to read an API key for a specific user.
    """
    try:
        api_key = api_key_manager.read_api_key(user_id)
        if api_key:
            return JSONResponse(
                content={
                    "api_key": api_key,
                    "message": "API key retrieved successfully",
                },
                status_code=200,
            )
        else:
            raise HTTPException(status_code=404, detail="API key not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
