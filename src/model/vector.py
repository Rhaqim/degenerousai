from typing import Optional

from pydantic import BaseModel, Field


class VectorStoreData(BaseModel):
    vector_store_id: str = Field(
        ..., description="The unique identifier for the vector store"
    )
    track_id: str = Field(
        ...,
        description="The identifier used for tracking the results, used as the name for the vector store",
    )
    callback_url: Optional[str] = Field(
        None, description="Optional callback URL for processing status updates"
    )
