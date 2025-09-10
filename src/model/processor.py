from pydantic import BaseModel, Field


class ProcessorDocumentURLRequest(BaseModel):
    url: str = Field(..., description="The URL of the document to process")
    track_id: str = Field(..., description="The ID of the tracking")
    callback_url: str = Field(..., description="The URL to call back after processing")
