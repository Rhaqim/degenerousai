from typing import Any, Dict, Optional

import httpx

from core.document.openai import DocumentProcessor
from model.topic import TopicDraft

api_key = "your_openai_api_key"
processor = DocumentProcessor(api_key=api_key)
# processor.process_url("https://example.com/document.pdf", "my_vector_store")
# if processor.check_file_status("my_vector_store"):
#     draft = processor.generate_topic_draft("my_vector_store")
#     print(draft)


async def process_url(vector_store_name: str, callback_url: str, url: str) -> str:
    processor.process_url(vector_store_name, callback_url, url)

    return "started"


async def process_file(
    vector_store_name: str,
    callback_url: str,
    file_bytes: bytes,
    file_type: str | None,
) -> str:
    # check that the file type is valid
    if file_type not in ["pdf", "txt", "doc", "docx"]:
        raise ValueError(
            "Invalid file type. Please upload a PDF, text, or Word document."
        )

    processor.process_byte_data(vector_store_name, callback_url, file_bytes)

    return "started"


def check_file_status(vector_store_name: str) -> Optional[TopicDraft]:
    if processor.check_file_status(vector_store_name):
        return processor.generate_topic_draft(vector_store_name)
    return None


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
