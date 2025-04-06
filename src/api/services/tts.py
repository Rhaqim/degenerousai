from core.tts.kokoro import KokotoTTS
from api.model.speech import CreateSpeechRequest

kokoro_tts = KokotoTTS()


def process_request(request: CreateSpeechRequest):
    """
    Process the TTS request and return the audio file path.
    """

    audio = kokoro_tts.process_request(
        text=request.input,
        lang_code=request.lang_code,
        voice=request.voice,
        speed=request.speed,
    )

    return audio
