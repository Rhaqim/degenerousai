from kokoro import KPipeline
import io
from typing import Optional
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

        # Initialize the TTS pipeline with the specified language code and repository ID
        self.english_pipeline = KPipeline(lang_code="a", repo_id=self.repo_id)

    def process_request(self, text: str, **kwargs):
        return self.generate_audio(text, **kwargs)

    def generate_audio(self, text: str, lang: str, voice: str) -> Optional[io.BytesIO]:
        """
        Generate audio from text using the specified language and voice.
        """
        if not text:
            raise ValueError("Text cannot be empty")

        lang_ = lang if lang in self.get_supported_languages() else "a"
        voice_ = voice if voice in self.get_supported_voices() else "af_heart"

        pipeline = self.get_pipeline(lang_)

        generator = pipeline(text, voice=voice_)

        for i, (ge, ps, audio) in enumerate(generator):
            if audio is not None:  # Check if audio is generated
                audio_buffer = io.BytesIO()
                sf.write(audio_buffer, audio, 24000, format="WAV")
                audio_buffer.seek(0)
                return audio_buffer
        return None

    def get_supported_languages(self):
        """
        Get the supported languages for the TTS service.
        """
        return ["en", "ja", "ko", "zh"]

    def get_supported_voices(self):
        """
        Get the supported voices for the TTS service.
        """
        return ["af_heart", "af_joy", "af_sad", "af_angry", "af_fear", "af_disgust"]

    def get_pipeline(self, lang_code) -> KPipeline:
        """
        Get the TTS pipeline for the specified language code.
        """
        if lang_code == "a":
            return self.english_pipeline

        else:
            raise ValueError(f"Unsupported language code: {lang_code}")
