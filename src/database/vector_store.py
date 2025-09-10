from typing import Optional

from model.vector import VectorStoreData, ProcessorStatus

from .main import Database


class VectorStore:
    def __init__(self):
        self.db = Database()
        self._migrate()

    def _migrate(self):
        """
        Creates the necessary tables in the database if they do not exist.
        """
        self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS vector_store_ids (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vector_store_id TEXT NOT NULL UNIQUE,
                vector_file_id TEXT,
                file_name TEXT,
                track_id TEXT NOT NULL UNIQUE,
                callback_url TEXT,
                status TEXT DEFAULT 'pending',
                error_message TEXT
            )
            """
        )

        self.db.commit()
        print("VectorStore database migration completed.")

    def create_vector_store_data(
        self, vector_store_id: str, track_id: str, callback_url: Optional[str] = None
    ):
        query = "INSERT INTO vector_store_ids (vector_store_id, track_id, callback_url) VALUES (?, ?, ?)"
        self.db.execute(query, (vector_store_id, track_id, callback_url))
        self.db.commit()

    def read_vector_store_data(self, track_id: str) -> Optional[VectorStoreData]:
        query = "SELECT vector_store_id, track_id, callback_url FROM vector_store_ids WHERE track_id = ?"
        result = self.db.fetch_one(query, (track_id,))
        return VectorStoreData(**result) if result else None

    def update_vector_file_data(
        self,
        track_id: str,
        vector_file_id: str,
        file_name: str,
        status: ProcessorStatus,
        error_message: Optional[str] = None,
    ):
        query = "UPDATE vector_store_ids SET vector_file_id = ?, file_name = ?, status = ?, error_message = ? WHERE track_id = ?"
        self.db.execute(
            query,
            (
                vector_file_id,
                file_name,
                status,
                error_message,
                track_id,
            ),
        )
        self.db.commit()

    def update_vector_store_data(
        self, track_id: str, new_vector_store_data: VectorStoreData
    ):
        query = "UPDATE vector_store_ids SET vector_store_id = ?, callback_url = ? WHERE track_id = ?"
        self.db.execute(
            query,
            (
                new_vector_store_data.vector_store_id,
                new_vector_store_data.callback_url,
                track_id,
            ),
        )
        self.db.commit()

    def delete_vector_store_data(self, track_id: str):
        query = "DELETE FROM vector_store_ids WHERE track_id = ?"
        self.db.execute(query, (track_id,))
        self.db.commit()
