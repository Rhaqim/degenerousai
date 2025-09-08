from abc import abstractmethod
import io
import os

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

    def convert_audio(
        self, audio: str | torch.FloatTensor, format: str = "WAV"
    ) -> io.BytesIO:
        """
        Convert audio to the specified format and return as BytesIO.
        """

        # Default sample rate (adjust as needed)
        DEFAULT_SAMPLERATE = 24000

        if isinstance(audio, torch.FloatTensor):
            audio_np = audio.numpy()
            samplerate = DEFAULT_SAMPLERATE  # Set default sample rate for tensor input
        elif isinstance(audio, str):
            # If audio is a string, assume it's a file path
            audio_np, samplerate = sf.read(audio)
        else:
            raise ValueError(
                "Unsupported audio format. Provide a valid audio file path or a tensor."
            )

        # Ensure directory exists
        # os.makedirs("audio", exist_ok=True)

        # # Save audio to file with correct format
        # audio_path = os.path.join("audio", "audio_output.wav")
        # sf.write(audio_path, audio_np, samplerate)

        # print(f"Audio saved to {audio_path}")

        # Save to BytesIO for return
        audio_buffer = io.BytesIO()
        sf.write(audio_buffer, audio_np, samplerate, format=format)
        audio_buffer.seek(0)

        return audio_buffer

    # def convcert_audio(self, audio: str | torch.FloatTensor, format: str) -> io.BytesIO:
    #     """
    #     Convert audio to the specified format.
    #     """

    #     if isinstance(audio, torch.FloatTensor):
    #         audio_np = audio.numpy()
    #     elif isinstance(audio, str):
    #         audio_np = np.frombuffer(audio.encode("utf-8"), dtype=np.float32)

    #     # write audio to a file with os
    #     # create directory if it does not exist
    #     os.makedirs("audio", exist_ok=True)
    #     # save audio to file
    #     audio_path = os.path.join("audio", f"audio.mp3")
    #     with open(audio_path, "wb") as f:
    #         f.write(audio_np.tobytes())
    #     print(f"Audio saved to {audio_path}")

    #     audio_buffer = io.BytesIO()
    #     sf.write(audio_buffer, audio_np, 24000, format=format)
    #     audio_buffer.seek(0)
    #     return audio_buffer

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
