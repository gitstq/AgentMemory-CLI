"""SQLite storage backend for AgentMemory.

Uses sqlite3 from the standard library with FTS5 full-text search support.
Provides thread-safe access via check_same_thread=False and a dedicated lock.
"""

from __future__ import annotations

import os
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from agentmemory.core.message import Message
from agentmemory.storage.base import StorageBackend


class SQLiteBackend(StorageBackend):
    """SQLite-based storage backend with FTS5 full-text search.

    Automatically creates the required tables on initialization.
    Thread safety is ensured via a threading.Lock.

    Attributes:
        store_path: Path to the SQLite database file.
    """

    def __init__(self, store_path: str = "./agentmemory_data/memory.db") -> None:
        """Initialize the SQLite storage backend.

        Creates the database file and tables if they do not exist.

        Args:
            store_path: Path to the SQLite database file. The parent
                directory will be created if needed.
        """
        self.store_path = store_path
        os.makedirs(os.path.dirname(store_path) or ".", exist_ok=True)
        self._lock = threading.Lock()
        self._conn: sqlite3.Connection = sqlite3.connect(
            store_path, check_same_thread=False
        )
        self._conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self) -> None:
        """Create the messages, sessions, and FTS tables."""
        with self._lock:
            cursor = self._conn.cursor()
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    metadata TEXT DEFAULT '{}'
                );

                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    message_count INTEGER DEFAULT 0,
                    tags TEXT DEFAULT '[]'
                );

                CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts
                USING fts5(id, session_id, role, content, timestamp, metadata,
                           content='messages', content_rowid='rowid');

                CREATE TRIGGER IF NOT EXISTS messages_ai
                AFTER INSERT ON messages BEGIN
                    INSERT INTO messages_fts(rowid, id, session_id, role,
                                             content, timestamp, metadata)
                    VALUES (new.rowid, new.id, new.session_id, new.role,
                            new.content, new.timestamp, new.metadata);
                END;

                CREATE TRIGGER IF NOT EXISTS messages_ad
                AFTER DELETE ON messages BEGIN
                    INSERT INTO messages_fts(messages_fts, rowid, id,
                                             session_id, role, content,
                                             timestamp, metadata)
                    VALUES ('delete', old.rowid, old.id, old.session_id,
                            old.role, old.content, old.timestamp,
                            old.metadata);
                END;

                CREATE TRIGGER IF NOT EXISTS messages_au
                AFTER UPDATE ON messages BEGIN
                    INSERT INTO messages_fts(messages_fts, rowid, id,
                                             session_id, role, content,
                                             timestamp, metadata)
                    VALUES ('delete', old.rowid, old.id, old.session_id,
                            old.role, old.content, old.timestamp,
                            old.metadata);
                    INSERT INTO messages_fts(rowid, id, session_id, role,
                                             content, timestamp, metadata)
                    VALUES (new.rowid, new.id, new.session_id, new.role,
                            new.content, new.timestamp, new.metadata);
                END;
            """)
            self._conn.commit()

    def save_message(self, message: Message) -> None:
        """Save a message to the SQLite database.

        Args:
            message: The Message object to save.
        """
        import json

        with self._lock:
            self._conn.execute(
                """INSERT OR REPLACE INTO messages
                   (id, session_id, role, content, timestamp, metadata)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    message.id,
                    message.session_id,
                    message.role,
                    message.content,
                    message.timestamp,
                    json.dumps(message.metadata),
                ),
            )
            self._conn.commit()

    def load_messages(
        self,
        session_id: str,
        limit: Optional[int] = None,
        offset: int = 0,
        role: Optional[str] = None,
    ) -> List[Message]:
        """Load messages from the SQLite database.

        Args:
            session_id: The session to load messages from.
            limit: Maximum number of messages to return.
            offset: Number of messages to skip.
            role: Optional role filter.

        Returns:
            A list of Message objects ordered by timestamp ascending.
        """
        import json

        with self._lock:
            query = "SELECT * FROM messages WHERE session_id = ?"
            params: list[Any] = [session_id]

            if role:
                query += " AND role = ?"
                params.append(role)

            query += " ORDER BY timestamp ASC"

            # SQLite requires LIMIT before OFFSET; use -1 for unlimited
            if limit is not None:
                query += " LIMIT ?"
                params.append(limit)

            if offset > 0:
                if limit is None:
                    query += " LIMIT -1"
                query += " OFFSET ?"
                params.append(offset)

            cursor = self._conn.execute(query, params)
            rows = cursor.fetchall()

        messages: List[Message] = []
        for row in rows:
            messages.append(
                Message(
                    id=row["id"],
                    role=row["role"],
                    content=row["content"],
                    timestamp=row["timestamp"],
                    metadata=json.loads(row["metadata"]),
                    session_id=row["session_id"],
                )
            )
        return messages

    def delete_message(self, message_id: str, session_id: str) -> bool:
        """Delete a message from the SQLite database.

        Args:
            message_id: The ID of the message to delete.
            session_id: The session the message belongs to.

        Returns:
            True if the message was deleted, False if not found.
        """
        with self._lock:
            cursor = self._conn.execute(
                "DELETE FROM messages WHERE id = ? AND session_id = ?",
                (message_id, session_id),
            )
            self._conn.commit()
            return cursor.rowcount > 0

    def search_messages(
        self,
        session_id: str,
        keyword: str,
        limit: Optional[int] = None,
    ) -> List[Message]:
        """Search messages using FTS5 full-text search.

        Args:
            session_id: The session to search in.
            keyword: The keyword to search for.
            limit: Maximum number of results.

        Returns:
            A list of matching Message objects.
        """
        import json

        with self._lock:
            # Use FTS5 for full-text search
            query = """
                SELECT m.* FROM messages m
                JOIN messages_fts fts ON m.id = fts.id
                WHERE fts.session_id = ? AND messages_fts MATCH ?
                ORDER BY m.timestamp ASC
            """
            params: list[Any] = [session_id, keyword]

            if limit is not None:
                query += " LIMIT ?"
                params.append(limit)

            try:
                cursor = self._conn.execute(query, params)
                rows = cursor.fetchall()
            except sqlite3.OperationalError:
                # FTS query failed, fall back to LIKE search
                query = """
                    SELECT * FROM messages
                    WHERE session_id = ? AND content LIKE ?
                    ORDER BY timestamp ASC
                """
                params = [session_id, f"%{keyword}%"]
                if limit is not None:
                    query += " LIMIT ?"
                    params.append(limit)
                cursor = self._conn.execute(query, params)
                rows = cursor.fetchall()

        messages: List[Message] = []
        for row in rows:
            messages.append(
                Message(
                    id=row["id"],
                    role=row["role"],
                    content=row["content"],
                    timestamp=row["timestamp"],
                    metadata=json.loads(row["metadata"]),
                    session_id=row["session_id"],
                )
            )
        return messages

    def get_session_list(self) -> List[Dict[str, Any]]:
        """Get a list of all sessions.

        Returns:
            A list of session metadata dictionaries.
        """
        with self._lock:
            cursor = self._conn.execute(
                "SELECT * FROM sessions ORDER BY updated_at DESC"
            )
            rows = cursor.fetchall()

        result: List[Dict[str, Any]] = []
        for row in rows:
            result.append(dict(row))
        return result

    def save_session_meta(self, session_id: str, meta: Dict[str, Any]) -> None:
        """Save or update session metadata.

        Args:
            session_id: The session ID.
            meta: The metadata dictionary.
        """
        import json

        with self._lock:
            self._conn.execute(
                """INSERT OR REPLACE INTO sessions
                   (session_id, name, created_at, updated_at,
                    message_count, tags)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    session_id,
                    meta.get("name", ""),
                    meta.get("created_at", datetime.now(timezone.utc).isoformat()),
                    meta.get(
                        "updated_at", datetime.now(timezone.utc).isoformat()
                    ),
                    meta.get("message_count", 0),
                    json.dumps(meta.get("tags", [])),
                ),
            )
            self._conn.commit()

    def load_session_meta(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load session metadata.

        Args:
            session_id: The session ID.

        Returns:
            A metadata dictionary, or None if not found.
        """
        import json

        with self._lock:
            cursor = self._conn.execute(
                "SELECT * FROM sessions WHERE session_id = ?",
                (session_id,),
            )
            row = cursor.fetchone()

        if row is None:
            return None

        result = dict(row)
        if "tags" in result and isinstance(result["tags"], str):
            result["tags"] = json.loads(result["tags"])
        return result

    def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its messages.

        Args:
            session_id: The session ID to delete.

        Returns:
            True if the session was deleted, False if not found.
        """
        with self._lock:
            cursor = self._conn.execute(
                "DELETE FROM messages WHERE session_id = ?", (session_id,)
            )
            cursor2 = self._conn.execute(
                "DELETE FROM sessions WHERE session_id = ?", (session_id,)
            )
            self._conn.commit()
            return cursor2.rowcount > 0

    def close(self) -> None:
        """Close the database connection."""
        with self._lock:
            if self._conn:
                self._conn.close()
                self._conn = None  # type: ignore[assignment]
