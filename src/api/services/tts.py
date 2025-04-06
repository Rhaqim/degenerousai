from core.tts.kokoro import KokotoTTS
from api.model.speech import CreateSpeechRequest

kokoro_tts = KokotoTTS()


def process_request(request: CreateSpeechRequest):
    """
    Process the TTS request and return the audio file path.
    """

    request.lang_code = "a"

    audio = kokoro_tts.process_request(
        text=request.input, lang=request.lang_code, voice=request.voice
    )

    # if request.stream:
    #     # Stream the audio response
    #     return StreamingResponse(
    #         response,
    #         media_type=f"audio/{request.response_format}",
    #         headers={"X-Download-Path": "streamed_audio"},
    #     )
    # else:
    #     # Save the audio file and return its path
    #     file_path = "/tmp/audio_response.mp3"  # Example path
    #     with open(file_path, "wb") as audio_file:
    #         audio_file.write(response.read())
    #     return JSONResponse(
    #         content={"audio_url": file_path},
    #         headers={"X-Download-Path": file_path},
    #     )

    return audio
