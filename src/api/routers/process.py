from fastapi import APIRouter, Form, UploadFile

from api.services.doc_processing import (
    process_file as call_openai_file,
    process_url as call_openai_url,
)

router = APIRouter(prefix="/process", tags=["Document Processing"])


@router.post("/document/file")
async def document_file(
    file: UploadFile, track_id: str = Form(...), callback_url: str = Form(...)
):
    # Step 1: Read and process the file
    content = await file.read()

    # Step 2: Send to OpenAI (pseudo-code)
    result = await call_openai_file(track_id, callback_url, content, file.content_type)

    return {"message": "Processing started", "status": result}


@router.post("/document/url")
async def document_url(
    url: str = Form(...), track_id: str = Form(...), callback_url: str = Form(...)
):
    # Step 1: Process the URL
    result = await call_openai_url(track_id, callback_url, url)

    return {"message": "Processing started", "status": result}


@router.post("/web/url")
async def web_url(
    url: str = Form(...), track_id: str = Form(...), callback_url: str = Form(...)
):
    # Step 1: Process the URL
    result = await call_openai_url(track_id, callback_url, url)

    return {"message": "Processing started", "status": result}
