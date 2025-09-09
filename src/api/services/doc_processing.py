import asyncio
from typing import Any, Dict, Optional

import httpx

from core.document.openai import DocumentProcessor
from model.topic import TopicDraft

api_key = "your_openai_api_key"
processor = DocumentProcessor(api_key=api_key)

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
) -> str:
    if file_type not in ["pdf", "txt", "doc", "docx"]:
        raise ValueError(
            "Invalid file type. Please upload a PDF, text, or Word document."
        )
    processor.process_byte_data(vector_store_name, callback_url, file_bytes)
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
