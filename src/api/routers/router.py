from fastapi import APIRouter, Form, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
import httpx

from model.chat_completions import ChatCompletionRequest, ChatCompletionResponse
from model.image import ImageRequest, ImageResponse
from model.speech import CreateSpeechRequest
from model.topic import TopicDraft
from model.video import VideoRequest, VideoResponse

from api.services.tts import process_request as tts_process_request
from api.services.ocr import parse_ocr
from api.services.doc_processing import process_file as call_openai

router = APIRouter()


@router.post("/audio/speech")
async def speech_to_text(request: CreateSpeechRequest):
    """
    Endpoint to handle speech-to-text generation.
    """
    try:
        audio = tts_process_request(request)
        if not audio:
            raise HTTPException(
                status_code=500, detail="Error processing audio request"
            )

        format = request.download_format or request.response_format or "wav"
        headers = {
            "Content-Disposition": f'attachment; filename="output.{format}"',
            "Content-Type": f"audio/{format}",
        }

        return StreamingResponse(audio, media_type=f"audio/{format}", headers=headers)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


ACCEPTED_TYPES = {
    "application/pdf": "pdf",
    "text/plain": "txt",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/msword": "doc",
}


@router.post("/ocr/topic", response_model=TopicDraft)
async def ocr_topic(request: UploadFile):
    """
    Endpoint to handle OCR processing for topic drafts.
    Accepts PDF, TXT, DOC, DOCX files.
    """
    try:
        if not request.content_type:
            raise HTTPException(
                status_code=400,
                detail="Content-Type header is missing. Please upload a valid file.",
            )

        file_type = ACCEPTED_TYPES.get(request.content_type)
        if not file_type:
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload a PDF, text, or Word document.",
            )

        file_bytes = await request.read()
        topic_draft = await parse_ocr(file_bytes, file_type)

        if not topic_draft:
            raise HTTPException(status_code=500, detail="Error processing OCR request")

        return topic_draft

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(request: ChatCompletionRequest):
    """
    Endpoint to handle chat completions following OpenAI's standard.
    """
    # Mock response for demonstration purposes
    try:
        response = {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": 1677652288,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Hello! How can I assist you?",
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20},
        }
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/images/generations", response_model=ImageResponse)
async def image_generations(request: ImageRequest):
    """
    Endpoint to handle image generations.
    """
    try:
        response = {
            "id": "imagecmpl-123",
            "object": "image.completion",
            "created": 1677652288,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Image processing completed successfully.",
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": 12,
                "completion_tokens": 12,
                "total_tokens": 24,
            },
        }
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/video/generations", response_model=VideoResponse)
async def video_generations(request: VideoRequest):
    """
    Endpoint to handle video generations.
    """
    try:
        response = {
            "id": "videocmpl-123",
            "object": "video.completion",
            "created": 1677652288,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Video processing completed successfully.",
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": 20,
                "completion_tokens": 20,
                "total_tokens": 40,
            },
        }
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process-file/")
async def process_file(
    file: UploadFile,
    vector_name: str = Form(...),
    callback_url: str = Form(...)
):
    # Step 1: Read and process the file
    content = await file.read()
    
    # Step 2: Send to OpenAI (pseudo-code)
    result = await call_openai(content, file.content_type, vector_name)

    # Step 3: Notify backend via webhook
    async with httpx.AsyncClient() as client:
        await client.post(callback_url, json={
            "vector_name": vector_name,
            "status": "completed",
            "result": result
        })

    return {"message": "Processing started"}
