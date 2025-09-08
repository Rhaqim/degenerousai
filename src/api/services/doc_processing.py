from typing import Optional
from core.document.openai import DocumentProcessor
from model.topic import TopicDraft

api_key = "your_openai_api_key"
processor = DocumentProcessor(api_key=api_key)
# processor.process_url("https://example.com/document.pdf", "my_vector_store")
# if processor.check_file_status("my_vector_store"):
#     draft = processor.generate_topic_draft("my_vector_store")
#     print(draft)


def process_url(url: str, vector_store_name: str):
    processor.process_url(url, vector_store_name)


async def process_file(
    file_bytes: bytes,
    file_type: str | None,
    vector_store_name: str = "default_vector_store",
) -> str:
    # check that the file type is valid
    if file_type not in ["pdf", "txt", "doc", "docx"]:
        raise ValueError(
            "Invalid file type. Please upload a PDF, text, or Word document."
        )

    processor.process_byte_data(file_bytes, vector_store_name)

    return "pending"


def check_file_status(vector_store_name: str) -> Optional[TopicDraft]:
    if processor.check_file_status(vector_store_name):
        return processor.generate_topic_draft(vector_store_name)
    return None
