from kokoro import KPipeline
import io
from typing import Optional

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

            for i, (ge, ps, audio) in enumerate(generator):
                if audio is not None:  # Check if audio is generated
                    return self.convcert_audio(audio, output_format)
            return None
        except Exception as e:
            print(f"Error generating audio: {e}")
            return None

    def get_supported_languages(self):
        """
        Get the supported languages for the TTS service.
        """
        return ["a", "j", "z"]

    def get_supported_voices(self):
        """
        Get the supported voices for the TTS service.
        """
        return ["af_heart", "af_joy", "af_sad", "af_angry", "af_fear", "af_disgust"]

    def get_pipeline(self, lang_code) -> KPipeline:
        """
        Get the TTS pipeline for the specified language code.
        """

        lang = lang_code if lang_code in self.get_supported_languages() else "a"

        # Initialize the TTS pipeline with the specified language code and repository ID
        return KPipeline(lang_code=lang, repo_id=self.repo_id)
