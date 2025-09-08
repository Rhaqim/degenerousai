from pydantic import BaseModel, Field
from typing import List, Optional, Literal

import json


class ChatCompletionMessage(BaseModel):
    """Message schema for OpenAI-compatible chat completion endpoint"""

    role: str
    content: str
    name: Optional[str] = None
    function_call: Optional[dict] = None


class ChatCompleteionResponseFormatJSONSchema(BaseModel):
    """Response format schema for OpenAI-compatible chat completion endpoint"""

    name: str = Field(
        ...,
        description="The name of the function to call. This should match the name of the function in the schema.",
    )
    description: str = Field(
        ...,
        description="A description of the function. This should be a human-readable explanation of what the function does.",
    )
    json_schema: str = Field( # TODO: Change to match a json encoding library
        ...,
        title="JSON Schema",
        description="The schema for the function. This should be a JSON schema that describes the parameters the function takes.",
    )
    strict: bool = False

class ChatCompleteionResponseFormat(BaseModel):
    """Response format schema for OpenAI-compatible chat completion endpoint"""

    type: Literal["json_object", "json_schema", "text"]
    JSONSchema: Optional[dict] = None


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatCompletionMessage]
    response_format: Optional[ChatCompleteionResponseFormat] = None
    temperature: Optional[float] = 1.0
    max_tokens: Optional[int] = 256


class ChatCompletionChoice(BaseModel):
    index: int
    message: ChatCompletionMessage
    finish_reason: Optional[str] = None


class ChatCompletionResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Optional[dict]
