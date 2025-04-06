from enum import Enum
from typing import Literal, Optional, Union

from pydantic import BaseModel, Field


class SpeechModel(str, Enum):
    """Enum for supported speech models"""

    TTS_1 = "tts-1"
    TTS_1_HD = "tts-1-hd"
    KOKORO = "kokoro"

    # convert string to enum
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: Union[str, "SpeechModel"]) -> "SpeechModel":
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError:
                raise ValueError(f"Invalid model: {value}")
        raise TypeError(f"Invalid type: {type(value)}. Expected str or Enum.")


class CreateSpeechRequest(BaseModel):
    """Request schema for OpenAI-compatible speech endpoint"""

    model: SpeechModel = Field(
        default=SpeechModel.KOKORO,
        title="Model",
        description="The model to use for generation. Supported models: tts-1, tts-1-hd, kokoro",
    )
    input: str = Field(..., description="The text to generate audio for")
    voice: str = Field(
        default="af_heart",
        description="The voice to use for generation. Can be a base voice or a combined voice name.",
    )
    response_format: Literal["mp3", "opus", "aac", "flac", "wav", "pcm"] = Field(
        default="mp3",
        description="The format to return audio in. Supported formats: mp3, opus, flac, wav, pcm. PCM format returns raw 16-bit samples without headers. AAC is not currently supported.",
    )
    download_format: Optional[Literal["mp3", "opus", "aac", "flac", "wav", "pcm"]] = (
        Field(
            default=None,
            description="Optional different format for the final download. If not provided, uses response_format.",
        )
    )
    speed: float = Field(
        default=1.0,
        ge=0.25,
        le=4.0,
        description="The speed of the generated audio. Select a value from 0.25 to 4.0.",
    )
    stream: bool = Field(
        default=True,  # Default to streaming for OpenAI compatibility
        description="If true (default), audio will be streamed as it's generated. Each chunk will be a complete sentence.",
    )
    return_download_link: bool = Field(
        default=False,
        description="If true, returns a download link in X-Download-Path header after streaming completes",
    )
    lang_code: Optional[str] = Field(
        default=None,
        description="Optional language code to use for text processing. If not provided, will use first letter of voice name.",
    )
