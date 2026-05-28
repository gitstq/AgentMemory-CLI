"""JSON file storage backend for AgentMemory.

Each session is stored as a separate JSON file. Atomic writes are achieved
by writing to a temporary file first, then renaming.
"""

from __future__ import annotations

import json
import os
import tempfile
from typing import Any, Dict, List, Optional

from agentmemory.core.message import Message
from agentmemory.storage.base import StorageBackend


class JSONBackend(StorageBackend):
    """JSON file-based storage backend.

    Stores each session as a separate JSON file in the specified directory.
    Session metadata is stored in a separate 'sessions.json' file.

    Attributes:
        store_path: Directory path where JSON files are stored.
    """

    def __init__(self, store_path: str = "./agentmemory_data") -> None:
        """Initialize the JSON file storage backend.

        Args:
            store_path: Path to the directory for storing JSON files.
                Will be created if it does not exist.
        """
        self.store_path = store_path
        os.makedirs(self.store_path, exist_ok=True)
        self._sessions_file = os.path.join(self.store_path, "sessions.json")

    def _session_file(self, session_id: str) -> str:
        """Get the file path for a session's messages.

        Args:
            session_id: The session ID.

        Returns:
            The absolute file path for the session JSON file.
        """
        return os.path.join(self.store_path, f"session_{session_id}.json")

    def _load_session_file(self, session_id: str) -> List[Dict[str, Any]]:
        """Load raw message dicts from a session file.

        Args:
            session_id: The session ID.

        Returns:
            A list of message dictionaries, or empty list if file not found.
        """
        filepath = self._session_file(session_id)
        if not os.path.exists(filepath):
            return []
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []

    def _save_session_file(
        self, session_id: str, data: List[Dict[str, Any]]
    ) -> None:
        """Atomically save message dicts to a session file.

        Writes to a temporary file first, then renames to ensure atomicity.

        Args:
            session_id: The session ID.
            data: The list of message dictionaries to save.
        """
        filepath = self._session_file(session_id)
        fd, tmp_path = tempfile.mkstemp(
            dir=self.store_path, suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, filepath)
        except Exception:
            # Clean up temp file on error
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise

    def _load_sessions_meta(self) -> Dict[str, Dict[str, Any]]:
        """Load all session metadata from the sessions file.

        Returns:
            A dictionary mapping session IDs to their metadata.
        """
        if not os.path.exists(self._sessions_file):
            return {}
        with open(self._sessions_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}

    def _save_sessions_meta(self, sessions: Dict[str, Dict[str, Any]]) -> None:
        """Atomically save all session metadata.

        Args:
            sessions: A dictionary mapping session IDs to metadata.
        """
        fd, tmp_path = tempfile.mkstemp(
            dir=self.store_path, suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(sessions, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, self._sessions_file)
        except Exception:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise

    def save_message(self, message: Message) -> None:
        """Save a message to the session's JSON file.

        Args:
            message: The Message object to save.
        """
        messages = self._load_session_file(message.session_id)
        messages.append(message.to_dict())
        self._save_session_file(message.session_id, messages)

    def load_messages(
        self,
        session_id: str,
        limit: Optional[int] = None,
        offset: int = 0,
        role: Optional[str] = None,
    ) -> List[Message]:
        """Load messages from a session's JSON file.

        Args:
            session_id: The session to load messages from.
            limit: Maximum number of messages to return.
            offset: Number of messages to skip.
            role: Optional role filter.

        Returns:
            A list of Message objects ordered by timestamp ascending.
        """
        raw = self._load_session_file(session_id)
        messages = [Message.from_dict(d) for d in raw]
        if role:
            messages = [m for m in messages if m.role == role]
        messages = sorted(messages, key=lambda m: m.timestamp)
        messages = messages[offset:]
        if limit is not None:
            messages = messages[:limit]
        return messages

    def delete_message(self, message_id: str, session_id: str) -> bool:
        """Delete a message from the session's JSON file.

        Args:
            message_id: The ID of the message to delete.
            session_id: The session the message belongs to.

        Returns:
            True if deleted, False if not found.
        """
        messages = self._load_session_file(session_id)
        original_len = len(messages)
        messages = [m for m in messages if m.get("id") != message_id]
        if len(messages) < original_len:
            self._save_session_file(session_id, messages)
            return True
        return False

    def search_messages(
        self,
        session_id: str,
        keyword: str,
        limit: Optional[int] = None,
    ) -> List[Message]:
        """Search messages by keyword in a session.

        Args:
            session_id: The session to search in.
            keyword: The keyword to search for (case-insensitive).
            limit: Maximum number of results.

        Returns:
            A list of matching Message objects.
        """
        messages = self.load_messages(session_id)
        keyword_lower = keyword.lower()
        results = [
            msg
            for msg in messages
            if keyword_lower in msg.content.lower()
        ]
        if limit is not None:
            results = results[:limit]
        return results

    def get_session_list(self) -> List[Dict[str, Any]]:
        """Get a list of all sessions.

        Returns:
            A list of session metadata dictionaries.
        """
        sessions = self._load_sessions_meta()
        return list(sessions.values())

    def save_session_meta(self, session_id: str, meta: Dict[str, Any]) -> None:
        """Save session metadata.

        Args:
            session_id: The session ID.
            meta: The metadata dictionary.
        """
        sessions = self._load_sessions_meta()
        sessions[session_id] = meta
        self._save_sessions_meta(sessions)

    def load_session_meta(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load session metadata.

        Args:
            session_id: The session ID.

        Returns:
            The metadata dictionary, or None if not found.
        """
        sessions = self._load_sessions_meta()
        return sessions.get(session_id)

    def delete_session(self, session_id: str) -> bool:
        """Delete a session and its files.

        Args:
            session_id: The session ID to delete.

        Returns:
            True if the session was deleted, False if not found.
        """
        sessions = self._load_sessions_meta()
        if session_id not in sessions:
            return False
        del sessions[session_id]
        self._save_sessions_meta(sessions)
        filepath = self._session_file(session_id)
        if os.path.exists(filepath):
            os.unlink(filepath)
        return True

    def close(self) -> None:
        """Release resources. No-op for JSON backend."""
        pass
