from typing import Optional

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
                vector_Store_id TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL UNIQUE
            )
            """
        )
        self.db.commit()
        print("VectorStore database migration completed.")

    def create_vector_store_id(self, vector_store_id: str, name: str):
        query = "INSERT INTO vector_store_ids (vector_Store_id, name) VALUES (?, ?)"
        self.db.execute(query, (vector_store_id, name))
        self.db.commit()

    def read_vector_store_id(self, name: str) -> Optional[str]:
        query = "SELECT vector_Store_id FROM vector_store_ids WHERE name = ?"
        result = self.db.fetch_one(query, (name,))
        return result["vector_Store_id"] if result else None

    def update_vector_store_id(self, name: str, new_vector_store_id: str):
        query = "UPDATE vector_store_ids SET vector_Store_id = ? WHERE name = ?"
        self.db.execute(query, (new_vector_store_id, name))
        self.db.commit()

    def delete_vector_store_id(self, name: str):
        query = "DELETE FROM vector_store_ids WHERE name = ?"
        self.db.execute(query, (name,))
        self.db.commit()
