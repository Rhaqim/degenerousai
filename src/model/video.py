from pydantic import BaseModel, Field
from typing import Literal, Optional


class VideoRequest(BaseModel):
    """Request schema for OpenAI-compatible video generation endpoint"""

    model: str = Field(
        default="video-gen",
        title="Model",
        description="The model to use for generation. Supported models: video-gen",
    )
    prompt: str = Field(..., description="The text prompt to generate videos for")
    n: int = Field(
        default=1,
        ge=1,
        le=10,
        description="The number of videos to generate. Must be between 1 and 10.",
    )
    size: Literal["256x256", "512x512", "1024x1024"] = Field(
        default="512x512",
        description="The size of the generated videos. Supported sizes: 256x256, 512x512, 1024x1024.",
    )
    response_format: Literal["url", "b64_json"] = Field(
        default="url",
        description="The format to return videos in. Supported formats: url, b64_json.",
    )
    user: Optional[str] = Field(
        default=None,
        description="An optional user ID to associate with the request. This can be used for tracking and analytics.",
    )


class VideoResponseData(BaseModel):
    """Response data schema for OpenAI-compatible video generation endpoint"""

    url: Optional[str] = Field(
        default=None,
        description="The URL of the generated video. Only present if response_format is 'url'.",
    )
    b64_json: Optional[str] = Field(
        default=None,
        description="The base64-encoded JSON of the generated video. Only present if response_format is 'b64_json'.",
    )


class VideoResponse(BaseModel):
    """Response schema for OpenAI-compatible video generation endpoint"""

    data: list[VideoResponseData]
    usage: Optional[dict] = Field(
        default=None,
        description="Optional usage information. This can include details about the request and response.",
    )
    error: Optional[dict] = Field(
        default=None,
        description="Optional error information. This can include details about any errors that occurred during processing.",
    )
    status: Optional[str] = Field(
        default=None,
        description="Optional status information. This can include details about the status of the request.",
    )
    model: Optional[str] = Field(
        default=None,
        description="Optional model information. This can include details about the model used for generation.",
    )
    id: Optional[str] = Field(
        default=None,
        description="Optional ID information. This can include details about the ID of the request.",
    )
    object: Optional[str] = Field(
        default=None,
        description="Optional object information. This can include details about the object used for generation.",
    )
    finish_reason: Optional[str] = Field(
        default=None,
        description="Optional finish reason information. This can include details about the reason for finishing the request.",
    )
    index: Optional[int] = Field(
        default=None,
        description="Optional index information. This can include details about the index of the request.",
    )
    prompt: Optional[str] = Field(
        default=None,
        description="Optional prompt information. This can include details about the prompt used for generation.",
    )
    model: Optional[str] = Field(
        default=None,
        description="Optional model information. This can include details about the model used for generation.",
    )
    object: Optional[str] = Field(
        default=None,
        description="Optional object information. This can include details about the object used for generation.",
    )
    created: Optional[int] = Field(
        default=None,
        description="Optional created information. This can include details about the creation time of the request.",
    )
