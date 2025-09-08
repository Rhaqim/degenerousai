from io import BytesIO
import requests
from typing import Optional

from openai import OpenAI

from database.vector_store import VectorStore
from model.topic import TopicDraft


class DocumentProcessor:
    """
    Handles uploading documents to OpenAI and associating them with a vector store.
    Supports processing from file paths, URLs, or raw byte data.
    """

    def __init__(self, client: Optional[OpenAI] = None, api_key: Optional[str] = None):
        """
        Initialize the DocumentProcessor with OpenAI API key and vector store database.
        """
        self.client = client or OpenAI(api_key=api_key)
        self.db = VectorStore()

    def get_or_create_vector_store_id(self, name: str) -> str:
        """
        Retrieve an existing vector store ID by name, or create a new one if it doesn't exist.
        """
        vec_store_id = self.db.read_vector_store_id(name)
        if vec_store_id:
            return vec_store_id

        vec_store = self.client.vector_stores.create(name=name)
        self.db.create_vector_store_id(vec_store.id, name)
        return vec_store.id

    def _upload_and_process(self, file_like, vector_store_name: str) -> None:
        """
        Upload a file-like object to OpenAI and associate it with the specified vector store.
        """
        upload_response = self.client.files.create(file=file_like, purpose="assistants")
        vector_store_id = self.get_or_create_vector_store_id(vector_store_name)
        self.client.vector_stores.files.create(
            file_id=upload_response.id, vector_store_id=vector_store_id
        )

    def process_file(self, file_path: str, vector_store_name: str) -> None:
        """
        Process a local file and associate it with a vector store.
        """
        with open(file_path, "rb") as f:
            self._upload_and_process(f, vector_store_name)

    def process_url(self, url: str, vector_store_name: str) -> None:
        """
        Download a file from a URL and associate it with a vector store.
        """
        response = requests.get(url)
        response.raise_for_status()
        file_like = BytesIO(response.content)
        self._upload_and_process(file_like, vector_store_name)

    def process_byte_data(self, byte_data: bytes, vector_store_name: str) -> None:
        """
        Process raw byte data and associate it with a vector store.
        """
        file_like = BytesIO(byte_data)
        self._upload_and_process(file_like, vector_store_name)

    def check_file_status(self, vector_store_id: str) -> bool:
        """
        Check the status of an uploaded file by its ID.
        """
        result = self.client.vector_stores.files.list(vector_store_id=vector_store_id)
        for file in result.data:
            if file.status == "completed":
                return True
        return False

    def generate_topic_draft(self, name: str) -> Optional["TopicDraft"]:
        """
        Generate a draft for a given topic using the associated vector store.
        """

        response = self.client.responses.parse(
            model="gpt-4o",
            input="Generate a topic draft based on the uploaded documents.",
            tools=[
                {
                    "type": "file_search",
                    "vector_store_ids": [self.get_or_create_vector_store_id(name)],
                }
            ],
            text_format=TopicDraft,
        )

        return response.output_parsed


# Example usage:
# api_key = "your_openai_api_key"
# processor = DocumentProcessor(api_key)
# processor.process_url("https://example.com/document.pdf", "my_vector_store")F
