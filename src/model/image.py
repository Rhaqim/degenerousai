from pydantic import BaseModel, Field
from typing import Literal, Optional


class ImageRequest(BaseModel):
    """Request schema for OpenAI-compatible image generation endpoint"""

    model: str = Field(
        default="dall-e",
        title="Model",
        description="The model to use for generation. Supported models: dall-e, dalle-2, dalle-3",
    )
    prompt: str = Field(..., description="The text prompt to generate images for")
    n: int = Field(
        default=1,
        ge=1,
        le=10,
        description="The number of images to generate. Must be between 1 and 10.",
    )
    size: Literal["256x256", "512x512", "1024x1024"] = Field(
        default="512x512",
        description="The size of the generated images. Supported sizes: 256x256, 512x512, 1024x1024.",
    )
    response_format: Literal["url", "b64_json"] = Field(
        default="url",
        description="The format to return images in. Supported formats: url, b64_json.",
    )
    user: Optional[str] = Field(
        default=None,
        description="An optional user ID to associate with the request. This can be used for tracking and analytics.",
    )


class ImageResponseData(BaseModel):
    """Response data schema for OpenAI-compatible image generation endpoint"""

    url: Optional[str] = Field(
        default=None,
        description="The URL of the generated image. Only present if response_format is 'url'.",
    )
    b64_json: Optional[str] = Field(
        default=None,
        description="The base64-encoded JSON of the generated image. Only present if response_format is 'b64_json'.",
    )


class ImageResponse(BaseModel):
    """Response schema for OpenAI-compatible image generation endpoint"""

    created: int
    data: list[ImageResponseData]
