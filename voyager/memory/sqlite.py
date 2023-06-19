import langchain
from pathlib import Path
import sqlite3
import os
import time
from typing import List

from voyager.memory.base import AgentMemoryInterface


class AgentMemorySQLite(AgentMemoryInterface):
    def __init__(self, db_path):
        super().__init__()

        assert db_path, "db_path must be provided"

        # check db_path's parent directory exists, if not, create it
        Path(os.path.dirname(db_path)).mkdir(parents=True, exist_ok=True)

        self.con = sqlite3.connect(db_path)
        self.cur = self.con.cursor()

        # Create table
        # | timestamp: int | name: str | role: str | topic: str | content: str | parent: int | id: int |
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS memory (
                timestamp INTEGER,
                name TEXT,
                role TEXT,
                topic TEXT,
                content TEXT,
                parent INTEGER,
                id INTEGER PRIMARY KEY AUTOINCREMENT
            )
            """
        )

    def save_messages(
        self,
        name: str,
        topic: str,
        messages: List[str],
        roles: List[str],
    ):
        def _insert_into_memory(
            timestamp: int,
            name: str,
            role: str,
            topic: str,
            content: str,
            parent: int,
        ) -> None:
            self.cur.execute(
                """
                INSERT INTO memory (timestamp, name, role, topic, content, parent)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    timestamp,
                    name,
                    role,
                    topic,
                    content,
                    parent,
                ),
            )
            self.con.commit()

        parent = None
        for message, role in zip(messages, roles):
            if not role:
                print(f"ignore unrecognized message with type {type(message)}")
                continue

            _insert_into_memory(
                int(time.time() * 1000),
                name,
                role,
                topic,
                message,
                parent if parent else -1,
            )
            parent = self.cur.lastrowid
