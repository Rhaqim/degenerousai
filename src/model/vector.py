from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ProcessorStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class VectorStoreData(BaseModel):
    vector_store_id: str = Field(
        ..., description="The unique identifier for the vector store"
    )
    vector_file_id: Optional[str] = Field(
        None, description="The identifier for the file in the vector store"
    )
    file_name: str = Field(..., description="The name of the file being processed")
    track_id: str = Field(
        ...,
        description="The identifier used for tracking the results, used as the name for the vector store",
    )
    callback_url: Optional[str] = Field(
        None, description="Optional callback URL for processing status updates"
    )
    status: ProcessorStatus = Field(
        ProcessorStatus.PENDING, description="The current status of the processing"
    )
    error_message: Optional[str] = Field(
        None, description="Error message if processing failed"
    )
