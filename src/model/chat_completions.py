from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any, Sequence, Union
import time
import uuid


# Available models
AVAILABLE_MODELS = [
    "openai/gpt-oss-20b",  # Smaller, more memory-friendly option
    "openai/gpt-oss-120b",  # Large model - requires significant VRAM
    "gpt2",  # Fallback option
    "gpt2-medium",  # Slightly larger fallback
    # Add more models here as they become available
]


class FunctionCall(BaseModel):
    name: str
    arguments: str  # JSON string


class RoleEnum(str, Enum):
    system = "system"
    user = "user"
    assistant = "assistant"
    function = "function"

    def __str__(self):
        return self.value


class ChatCompletionMessage(BaseModel):
    role: RoleEnum
    content: Optional[str] = None
    name: Optional[str] = None
    function_call: Optional[FunctionCall] = None


class ChatCompletionResponseFormatJSONSchema(BaseModel):
    """Response format schema for OpenAI-compatible chat completion endpoint"""

    name: str = Field(
        ...,
        description="The name of the function to call. This should match the name of the function in the schema.",
    )
    description: str = Field(
        ...,
        description="A description of the function. This should be a human-readable explanation of what the function does.",
    )
    json_schema: Dict[str, Any] = Field(
        ...,
        title="JSON Schema",
        description="The schema for the function. This should be a JSON schema that describes the parameters the function takes.",
    )
    strict: bool = False


class ChatCompletionResponseFormat(BaseModel):
    """Response format schema for OpenAI-compatible chat completion endpoint"""

    type: Literal["json_object", "json_schema", "text"]
    json_schema: Optional[ChatCompletionResponseFormatJSONSchema] = None


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatCompletionMessage]
    response_format: Optional[ChatCompletionResponseFormat] = None
    temperature: Optional[float] = 1.0
    max_tokens: Optional[int] = 256


class ChatCompletionChoice(BaseModel):
    index: int
    message: ChatCompletionMessage
    finish_reason: Optional[
        Literal["stop", "length", "function_call", "content_filter"]
    ] = None


class ChatCompletionUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Optional[ChatCompletionUsage]


# Available models
AVAILABLE_MODELS = [
    "openai/gpt-oss-20b",
    # Add more models here as they become available
]


class ChatCompletions:
    """Chat completions handler with OpenAI-compatible interface"""

    @staticmethod
    def get_available_models() -> List[str]:
        """Get list of available models"""
        return AVAILABLE_MODELS

    @staticmethod
    def create(request: ChatCompletionRequest) -> ChatCompletionResponse:
        """
        Create a chat completion using the specified model and parameters.

        Args:
            request: ChatCompletionRequest containing model, messages, and parameters

        Returns:
            ChatCompletionResponse with the model's response

        Raises:
            ValueError: If the specified model is not available
        """
        if request.model not in AVAILABLE_MODELS:
            raise ValueError(
                f"Model '{request.model}' not available. Available models: {AVAILABLE_MODELS}"
            )

        # Import here to avoid circular imports
        from src.core.chat.openai import OpenAIChat

        # Initialize the chat model
        chat_model = OpenAIChat(model=request.model)

        # Convert messages to the format expected by the chat model
        messages = []
        for msg in request.messages:
            message_dict = {"role": msg.role, "content": msg.content}
            if msg.name:
                message_dict["name"] = msg.name
            if msg.function_call:
                message_dict["function_call"] = {
                    "name": msg.function_call.name,
                    "arguments": msg.function_call.arguments,
                }
            messages.append(message_dict)

        # Generate response using the chat model
        raw_response = chat_model.chat(
            messages=messages,
            max_tokens=request.max_tokens if request.max_tokens else 256,
            temperature=request.temperature if request.temperature else 1.0,
        )

        # Convert response to ChatCompletionResponse format
        response_id = f"chatcmpl-{uuid.uuid4().hex[:29]}"
        created_timestamp = int(time.time())

        # Extract the generated content
        if "choices" in raw_response and raw_response["choices"]:
            generated_content = raw_response["choices"][0]["message"]["content"]

            # Clean up the content - remove the original prompt if it's included
            # This is a simple heuristic to extract just the assistant's response
            if "assistant:" in generated_content.lower():
                parts = generated_content.split("assistant:", 1)
                if len(parts) > 1:
                    generated_content = parts[1].strip()
        else:
            generated_content = "No response generated"

        # Create response message
        response_message = ChatCompletionMessage(
            role=RoleEnum.assistant, content=generated_content
        )

        # Create choice
        choice = ChatCompletionChoice(
            index=0, message=response_message, finish_reason="stop"
        )

        # Estimate usage (simplified for now)
        prompt_tokens = sum(
            len(msg.content.split()) if msg.content else 0 for msg in request.messages
        )
        completion_tokens = len(generated_content.split()) if generated_content else 0
        total_tokens = prompt_tokens + completion_tokens

        usage = ChatCompletionUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
        )

        return ChatCompletionResponse(
            id=response_id,
            object="chat.completion",
            created=created_timestamp,
            model=request.model,
            choices=[choice],
            usage=usage,
        )


# Convenience function for direct usage
def create_chat_completion(
    model: str,
    messages: Sequence[Union[Dict[str, str], Dict[str, Dict[str, str]]]],
    temperature: Optional[float] = 1.0,
    max_tokens: Optional[int] = 256,
    response_format: Optional[ChatCompletionResponseFormat] = None,
) -> ChatCompletionResponse:
    """
    Convenience function to create a chat completion.

    Args:
        model: The model to use for completion
        messages: List of message dictionaries with 'role' and 'content'
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        response_format: Format for the response

    Returns:
        ChatCompletionResponse
    """
    # Convert dict messages to ChatCompletionMessage objects
    completion_messages = []
    for msg in messages:
        # Validate role to ensure it matches allowed values
        allowed_roles = {"system", "user", "assistant", "function"}
        role_value = msg["role"]
        if role_value not in allowed_roles:
            raise ValueError(
                f"Invalid role: {role_value}. Allowed roles: {allowed_roles}"
            )

        # Ensure content is str or None
        content_val = msg.get("content")
        if isinstance(content_val, dict):
            content = str(content_val)
        elif isinstance(content_val, str) or content_val is None:
            content = content_val
        else:
            content = str(content_val) if content_val is not None else None

        # Ensure name is str or None
        name_val = msg.get("name")
        if isinstance(name_val, dict):
            name = str(name_val)
        elif isinstance(name_val, str) or name_val is None:
            name = name_val
        else:
            name = str(name_val) if name_val is not None else None

        # Ensure function_call is constructed only if it's a dict with required keys
        function_call_obj = None
        fc_val = msg.get("function_call")
        if isinstance(fc_val, dict):
            fc_name = fc_val.get("name")
            fc_args = fc_val.get("arguments")
            if isinstance(fc_name, str) and isinstance(fc_args, str):
                function_call_obj = FunctionCall(name=fc_name, arguments=fc_args)

        completion_messages.append(
            ChatCompletionMessage(
                role=RoleEnum(role_value),  # Convert string to RoleEnum
                content=content,
                name=name,
                function_call=function_call_obj,
            )
        )

    request = ChatCompletionRequest(
        model=model,
        messages=completion_messages,
        temperature=temperature,
        max_tokens=max_tokens,
        response_format=response_format,
    )

    return ChatCompletions.create(request)
