import asyncio
from typing import Any, Dict, Optional

import httpx

from config.keys import OPENAI_API_KEY
from core.processor.openai import Processor
from model.topic import TopicDraft


processor = Processor(api_key=OPENAI_API_KEY)

POLL_INTERVAL = 5  # seconds


async def poll_status_and_callback(vector_store_name: str):
    while True:
        result = processor.check_file_status(vector_store_name)
        if (
            result["status"] == "completed"
            and result["callback_url"]
            and result["result"]
        ):
            await callback_webhook(
                result["callback_url"],
                vector_store_name,
                result["status"],
                result["result"],
            )
            break
        await asyncio.sleep(POLL_INTERVAL)


async def process_url(vector_store_name: str, callback_url: str, url: str) -> str:
    processor.process_url(vector_store_name, callback_url, url)
    asyncio.create_task(poll_status_and_callback(vector_store_name))
    return "started"


async def process_file(
    vector_store_name: str,
    callback_url: str,
    file_bytes: bytes,
    file_type: str | None,
    file_name: str | None = "uploaded_file",
) -> str:
    print(f"Processing file of type: {file_type}")
    if file_type not in ["application/pdf", "application/txt", "application/doc", "application/docx"]:
        raise ValueError(
            f"Invalid file type. Please upload a PDF, text, or Word document. Given: {file_type}"
        )
    
    if not file_name:
        file_name = "uploaded_file"
    
    processor.process_byte_data(vector_store_name, callback_url, file_bytes, file_name)

    print(f"Started processing for vector store: {vector_store_name}")
    asyncio.create_task(poll_status_and_callback(vector_store_name))
    return "started"


async def callback_webhook(
    url: str, vector_name: str, status: str, result: Optional[TopicDraft] = None
):
    async with httpx.AsyncClient() as client:
        payload: Dict[str, Any] = {
            "track_id": vector_name,
            "status": status,
        }
        if result:
            payload["result"] = result
        await client.post(url, json=payload)
