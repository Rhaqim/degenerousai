import json
from typing import List, Optional

from model.topic import TopicDraft

from .main import Database


class TopicDraftDB:
    def __init__(self):
        self.db = Database()
        self._migrate()

    def _migrate(self):
        """
        Creates the necessary tables in the database if they do not exist.
        """

        print("Migrating TopicDraft database...")
        self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS topic_drafts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                story_data TEXT,
                open_prompt TEXT,
                table_prompt TEXT,
                file_name TEXT UNIQUE,
                vector_store_id TEXT,
                FOREIGN KEY (vector_store_id) REFERENCES vector_store_ids(vector_store_id)
            )
            """
        )
        self.db.commit()
        print("TopicDraft database migration completed.")

    def create_topic_draft(
        self, topic_draft: TopicDraft, vector_store_id: Optional[str] = None
    ):
        query = "INSERT INTO topic_drafts (title, story_data, open_prompt, table_prompt, vector_store_id) VALUES (?, ?, ?, ?, ?)"
        story_data_json = (
            topic_draft.story_data.model_dump_json() if topic_draft.story_data else None
        )
        table_prompt_json = (
            topic_draft.table_prompt.model_dump_json()
            if topic_draft.table_prompt
            else None
        )
        self.db.execute(
            query,
            (
                topic_draft.title,
                story_data_json,
                topic_draft.open_prompt,
                table_prompt_json,
                vector_store_id,
            ),
        )
        self.db.commit()

    def read_topic_draft(self, vector_store_id: str) -> Optional[List[TopicDraft]]:
        query = "SELECT * FROM topic_drafts WHERE vector_store_id = ?"
        result = self.db.fetch_all(query, (vector_store_id,))
        if result:
            return [
                TopicDraft(
                    title=row["title"],
                    story_data=json.loads(row["story_data"]) if row["story_data"] else None,
                    open_prompt=row["open_prompt"],
                    table_prompt=json.loads(row["table_prompt"]) if row["table_prompt"] else None,
                )
                for row in result
            ]
        return None
        #     story_data = (
        #         json.loads(result["story_data"]) if result["story_data"] else None
        #     )
        #     table_prompt = (
        #         json.loads(result["table_prompt"]) if result["table_prompt"] else None
        #     )
        #     return TopicDraft(
        #         title=result["title"],
        #         story_data=story_data,
        #         open_prompt=result["open_prompt"],
        #         table_prompt=table_prompt,
        #     )
        # return None

    def update_topic_draft(self, title: str, updated_topic_draft: TopicDraft):
        query = "UPDATE topic_drafts SET story_data = ?, open_prompt = ?, table_prompt = ? WHERE title = ?"
        story_data_json = (
            json.dumps(updated_topic_draft.story_data.dict())
            if updated_topic_draft.story_data
            else None
        )
        table_prompt_json = (
            json.dumps(updated_topic_draft.table_prompt.dict())
            if updated_topic_draft.table_prompt
            else None
        )
        self.db.execute(
            query,
            (
                story_data_json,
                updated_topic_draft.open_prompt,
                table_prompt_json,
                title,
            ),
        )
        self.db.commit()

    def delete_topic_draft(self, title: str):
        query = "DELETE FROM topic_drafts WHERE title = ?"
        self.db.execute(query, (title,))
        self.db.commit()
