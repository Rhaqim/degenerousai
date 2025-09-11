from io import BytesIO
import requests
from typing import Any, Dict, Optional, Tuple

from openai import OpenAI

from database.vector_store import VectorStore
from database.topic_draft import TopicDraftDB
from model.topic import TopicDraft
from model.vector import ProcessorStatus


class Processor:
    """
    Handles uploading documents to OpenAI and associating them with a vector store.
    Supports processing from file paths, URLs, or raw byte data. ALso handles processing web links.
    """

    def __init__(
        self,
        client: Optional[OpenAI] = None,
        api_key: Optional[str] = None,
        vector_db: Optional[VectorStore] = None,
        topic_db: Optional[TopicDraftDB] = None,
    ):
        """
        Initialize the DocumentProcessor with OpenAI API key and vector store database.
        """
        self.client = client or OpenAI(api_key=api_key)
        self.db = vector_db or VectorStore()
        self.topic_db = topic_db or TopicDraftDB()
        # Optionally call self._migrate() here if needed

    def _migrate(self):
        """
        Ensures the necessary database tables are created.
        """
        self.db._migrate()
        self.topic_db._migrate()

    def get_or_create_vector_store_id(
        self, name: str, callback_url: str
    ) -> Tuple[str, Optional[str]]:
        """
        Retrieve an existing vector store ID by name, or create a new one if it doesn't exist.
        """

        print(f"Retrieving or creating vector store with name: {name}")
        vec_store = self.db.read_vector_store_data(name)
        if vec_store:
            return (vec_store.vector_store_id, vec_store.vector_file_id)

        vec_store = self.client.vector_stores.create(name=name)
        self.db.create_vector_store_data(vec_store.id, name, callback_url)
        return (vec_store.id, None)

    def _upload_and_process(
        self, file_like: Tuple[str, bytes], vector_store_name: str, callback_url: str
    ) -> None:
        """
        Upload a file-like object to OpenAI and associate it with the specified vector store.
        """

        print(f"Uploading and processing file for vector store: {vector_store_name}")

        vector_store_id, vector_file_id = self.get_or_create_vector_store_id(
            vector_store_name, callback_url
        )

        if vector_file_id:
            print(
                f"File already associated with vector store '{vector_store_name}'. Skipping upload."
            )
            return

        upload_response = self.client.files.create(file=file_like, purpose="assistants")

        print(
            f"Uploaded file with ID: {upload_response.id} Using vector store ID: {vector_store_id}"
        )

        self.client.vector_stores.files.create(
            file_id=upload_response.id, vector_store_id=vector_store_id
        )

        print(f"File associated with vector store: {vector_store_name}")

        self.db.update_vector_file_data(
            vector_store_name,
            upload_response.id,
            file_like[0],
            ProcessorStatus.PROCESSING,
        )

    def process_file(
        self, file_path: str, vector_store_name: str, callback_url: str
    ) -> None:
        """
        Process a local file and associate it with a vector store.
        """
        with open(file_path, "rb") as f:
            file_like = BytesIO(f.read())
            file_name = file_path.split("/")[-1]
            file_tuple = (file_name, file_like.getvalue())
            self._upload_and_process(file_tuple, vector_store_name, callback_url)

    def process_url(self, vector_store_name: str, callback_url: str, url: str) -> None:
        """
        Download a file from a URL and associate it with a vector store.
        """
        response = requests.get(url)
        response.raise_for_status()
        file_like = BytesIO(response.content)
        file_name = url.split("/")[-1] or "downloaded_file"
        file_tuple = (file_name, file_like.getvalue())
        self._upload_and_process(file_tuple, vector_store_name, callback_url)

    def process_byte_data(
        self,
        vector_store_name: str,
        callback_url: str,
        byte_data: bytes,
        file_name: str = "uploaded_file",
    ) -> None:
        """
        Process raw byte data and associate it with a vector store.
        """

        # print(f"Processing byte data of size: {len(byte_data)} bytes")
        # file_like = BytesIO(byte_data)
        # file_like.name = "uploaded_file"
        file_tuple = (file_name, byte_data)
        self._upload_and_process(file_tuple, vector_store_name, callback_url)

    def check_file_status(self, vector_store_name: str) -> Dict[str, Any]:
        """
        Check the status of uploaded files by vector store name.
        Returns a dict with 'status' and 'result' keys.
        """
        vector_store = self.db.read_vector_store_data(vector_store_name)

        if not vector_store:
            raise ValueError(f"Vector store with name '{vector_store_name}' not found.")

        result = self.client.vector_stores.files.list(
            vector_store_id=vector_store.vector_store_id
        )

        for file in result.data:
            if file.status == "completed":

                draft = self.generate_topic_draft(vector_store.vector_store_id)
                return {
                    "status": "completed",
                    "result": draft,
                    "callback_url": vector_store.callback_url,
                }
        # If no file is completed, return the status of the last file (or None)
        last_status = result.data[-1].status if result.data else None
        return {"status": last_status, "result": None}

    def generate_topic_draft(self, vector_store_id: str) -> Optional[TopicDraft]:
        """
        Generate a draft for a given topic using the associated vector store.
        """

        # try and get the topic draft from the database first
        existing_draft = self.topic_db.read_topic_draft(vector_store_id)
        if existing_draft:
            return existing_draft[0]  # return the first draft if multiple exist

        response = self.client.responses.parse(
            model="gpt-4o",
            input=[
                {
                    "role": "system",
                    "content": "Generate a topic draft based on the uploaded documents.",
                },
                {
                    "role": "user",
                    "content": "Please create a comprehensive topic draft using the information from the documents.",
                },
            ],
            tools=[
                {
                    "type": "file_search",
                    "vector_store_ids": [vector_store_id],
                }
            ],
            text_format=TopicDraft,
        )

        # store the generated topic draft in the database
        if response.output_parsed:
            self.topic_db.create_topic_draft(
                response.output_parsed, vector_store_id=vector_store_id
            )

        return response.output_parsed


# Example usage:
# api_key = "your_openai_api_key"
# processor = DocumentProcessor(api_key=api_key)
# processor.process_url("https://example.com/document.pdf", "my_vector_store")
# if processor.check_file_status("my_vector_store"):
#     draft = processor.generate_topic_draft("my_vector_store")
#     print(draft)
