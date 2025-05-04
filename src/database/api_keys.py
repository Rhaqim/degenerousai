from .main import Database


class APIKeyManager:
    def __init__(self):
        self.db = Database()

        self._migrate()

    def _migrate(self):
        """
        Creates the necessary tables in the database if they do not exist.
        """
        self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                api_key TEXT NOT NULL
            )
            """
        )
        self.db.commit()
        print("Database migration completed.")

    def create_api_key(self, user_id, api_key):
        query = "INSERT INTO api_keys (user_id, api_key) VALUES (?, ?)"
        self.db.execute(query, (user_id, api_key))
        self.db.commit()

    def read_api_key(self, user_id):
        query = "SELECT api_key FROM api_keys WHERE user_id = ?"
        result = self.db.fetch_one(query, (user_id,))
        return result["api_key"] if result else None

    def update_api_key(self, user_id, new_api_key):
        query = "UPDATE api_keys SET api_key = ? WHERE user_id = ?"
        self.db.execute(query, (new_api_key, user_id))
        self.db.commit()

    def delete_api_key(self, user_id):
        query = "DELETE FROM api_keys WHERE user_id = ?"
        self.db.execute(query, (user_id,))
        self.db.commit()
