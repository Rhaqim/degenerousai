from fastapi import APIRouter, Form, UploadFile

from api.services.processor import (
    process_file as call_openai_file,
    process_url as call_openai_url,
)
from model.processor import ProcessorDocumentURLRequest

router = APIRouter(prefix="/process", tags=["Document Processing"])


@router.post("/document/file")
async def document_file(
    file: UploadFile, track_id: str = Form(...), callback_url: str = Form(...)
):
    # Step 1: Read and process the file
    content = await file.read()

    print(
        f"Received file: {file.filename}, type: {file.content_type} with size {len(content)} bytes"
    )
    print(f"Task ID: {track_id}, Callback URL: {callback_url}")

    # Step 2: Send to OpenAI (pseudo-code)
    result = await call_openai_file(
        track_id, callback_url, content, file.content_type, file.filename,
    )

    return {"message": "Processing started", "status": result}


@router.post("/document/url")
async def document_url(request: ProcessorDocumentURLRequest):
    url = request.url
    track_id = request.track_id
    callback_url = request.callback_url

    # Step 1: Process the URL
    result = await call_openai_url(track_id, callback_url, url)

    return {"message": "Processing started", "status": result}


@router.post("/web/url")
async def web_url(request: ProcessorDocumentURLRequest):
    # Step 1: Process the URL
    result = await call_openai_url(request.track_id, request.callback_url, request.url)

    return {"message": "Processing started", "status": result}
