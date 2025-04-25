from kokoro import KModel, KPipeline
import io
import os
import torch
from typing import Optional
import numpy as np
import soundfile as sf

from core.interface.texttospeech import TextToSpeechServiceBase


class KokotoTTS(TextToSpeechServiceBase):
    """
    KokotoTTS is a text-to-speech service that uses the Kokoro library to generate audio from text.
    """

    def __init__(self):
        """
        Initialize the KokotoTTS service.
        """

        self.repo_id = "hexgrad/Kokoro-82M"
        self._model = None
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = "kokoro-v1_0.pth"

        # self.load_model()

    def process_request(
        self, text: str, lang_code: str | None, voice: str, speed: float = 1.0
    ):
        lang_code = lang_code if lang_code else "a"
        return self.generate_audio(text, lang_code, voice, speed)
    


    def generate_audio(
        self,
        text: str,
        lang_code: str,
        voice: str,
        speed: float = 1.0,
        output_format: str = "wav",
    ) -> Optional[io.BytesIO]:
        """
        Generate audio from text using the specified language and voice.
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        voice_ = voice if voice in self.get_supported_voices() else "af_heart"

        try:
            pipeline = self.get_pipeline(lang_code)
            generator = pipeline(text, voice=voice_, speed=speed)

            audio_list = []
            sample_rate = 24000  # Default sample rate

            # Collect all audio segments
            for i, (_, _, audio) in enumerate(generator):
                if audio is not None:  # Check if audio is generated
                    audio_list.append(audio)

            if not audio_list:
                raise ValueError("No audio data was generated.")

            # Combine audio arrays
            combined_audio_np = np.concatenate(audio_list)

            # Save to BytesIO
            audio_buffer = io.BytesIO()
            sf.write(audio_buffer, combined_audio_np, sample_rate, format=output_format)
            audio_buffer.seek(0)

            return audio_buffer

        except Exception as e:
            print(f"Error generating audio: {e}")
            return None

    def load_model(self, path: str = "models") -> None:
        """Load pre-baked model.

        Args:
            path: Path to model file

        Raises:
            RuntimeError: If model loading fails
        """
        try:
            # Get verified model path
            # model_path = os.path.abspath(path)
            # model is located one folder abover called models
            model_path = os.path.join(os.path.dirname(__file__), "..", path, self.model_name)
            if not os.path.exists(model_path):
                raise RuntimeError(f"Model file not found: {model_path}")

            # Get config path
            # Assuming the config file is in the same directory as the model file
            # and named "config.json"
            config_path = os.path.join(os.path.dirname(model_path), "config.json")

            if not os.path.exists(config_path):
                raise RuntimeError(f"Config file not found: {config_path}")

            print(f"Loading Kokoro model on {self._device}")
            print(f"Config path: {config_path}")
            print(f"Model path: {model_path}")

            # Load model and let KModel handle device mapping
            self._model = KModel(config=config_path, model=model_path).eval()
            # For MPS, manually move ISTFT layers to CPU while keeping rest on MPS
            if self._device == "mps":
                print(
                    "Moving model to MPS device with CPU fallback for unsupported operations"
                )
                self._model = self._model.to(torch.device("mps"))
            elif self._device == "cuda":
                self._model = self._model.cuda()
            else:
                self._model = self._model.cpu()

        except FileNotFoundError as e:
            raise e
        except Exception as e:
            raise RuntimeError(f"Failed to load Kokoro model: {e}")

    def unload_model(self) -> None:
        """Unload the model.

        Raises:
            RuntimeError: If model unloading fails
        """
        try:
            if self._model is not None:
                del self._model
                self._model = None
                print("Model unloaded successfully.")
            else:
                print("No model to unload.")
        except Exception as e:
            raise RuntimeError(f"Failed to unload Kokoro model: {e}")
        self._model = None

    def get_supported_languages(self):
        """
        Get the supported languages for the TTS service.
        """
        return ["a", "j", "z"]

    def get_supported_voices(self):
        """
        Get the supported voices for the TTS service.
        """
        names = [
                "af_alloy",
                "af_bella",
                "af_heart",
                "af_jessica",
                "af_kore",
                "af_nicole",
                "af_nova",
                "af_river",
                "af_sarah",
                "af_sky",
                "am_echo",
                "am_eric",
                "am_fenrir",
                "am_liam",
                "am_michael",
                "am_onyx",
                "am_puck",
                "am_santa"
            ]
        return names

    def get_pipeline(self, lang_code) -> KPipeline:
        """
        Get the TTS pipeline for the specified language code.
        """

        lang = lang_code if lang_code in self.get_supported_languages() else "a"

        if self._model is not None:
            # Use the loaded model if available
            print(f"Using loaded model for language: {lang}")
            return KPipeline(lang_code=lang, repo_id=self.repo_id, model=self._model)

        # Initialize the TTS pipeline with the specified language code and repository ID
        return KPipeline(lang_code=lang, repo_id=self.repo_id)
