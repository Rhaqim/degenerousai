from abc import abstractmethod
import io

import numpy as np
import torch
import soundfile as sf

from core.interface.base import AIServiceBase


class TextToSpeechServiceBase(AIServiceBase):
    """
    Base class for text-to-speech AI services.
    """

    @abstractmethod
    def process_request(
        self, text: str, lang_code: str, voice: str, speed: float = 1.0, **kwargs
    ):
        """
        Abstract method to process text-to-speech requests.
        Must be implemented by subclasses.
        """
        pass

    def convcert_audio(self, audio: str | torch.FloatTensor, format: str) -> io.BytesIO:
        """
        Convert audio to the specified format.
        """

        if isinstance(audio, torch.FloatTensor):
            audio_np = audio.numpy()
        elif isinstance(audio, str):
            audio_np = np.frombuffer(audio.encode("utf-8"), dtype=np.float32)

        audio_buffer = io.BytesIO()
        sf.write(audio_buffer, audio_np, 24000, format=format)
        audio_buffer.seek(0)
        return audio_buffer

    def get_supported_format(self, format: str = "WAV") -> str:
        """
        Get supported audio formats.
        """
        sf_fornmats = sf.available_formats()

        # convert format to uppercase
        format = format.upper()
        if format not in sf_fornmats:
            return "WAV"
        return format
