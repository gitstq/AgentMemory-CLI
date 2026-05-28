"""In-memory storage backend for testing and temporary use."""

from __future__ import annotations

import threading
from typing import Any, Dict, List, Optional

from agentmemory.core.message import Message
from agentmemory.storage.base import StorageBackend


class MemoryBackend(StorageBackend):
    """In-memory storage backend using Python dictionaries.

    This backend stores all data in memory and does not persist across
    restarts. It is primarily intended for testing and temporary usage.

    Thread safety is provided via a threading.Lock.
    """

    def __init__(self, store_path: str = "") -> None:
        """Initialize the in-memory storage.

        Args:
            store_path: Ignored for MemoryBackend, accepted for interface
                compatibility.
        """
        self._messages: Dict[str, List[Message]] = {}
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def save_message(self, message: Message) -> None:
        """Save a message to in-memory storage.

        Args:
            message: The Message object to save.
        """
        with self._lock:
            sid = message.session_id
            if sid not in self._messages:
                self._messages[sid] = []
            self._messages[sid].append(message)

    def load_messages(
        self,
        session_id: str,
        limit: Optional[int] = None,
        offset: int = 0,
        role: Optional[str] = None,
    ) -> List[Message]:
        """Load messages from in-memory storage.

        Args:
            session_id: The session to load messages from.
            limit: Maximum number of messages to return.
            offset: Number of messages to skip.
            role: Optional role filter.

        Returns:
            A list of Message objects ordered by timestamp ascending.
        """
        with self._lock:
            messages = self._messages.get(session_id, [])
            if role:
                messages = [m for m in messages if m.role == role]
            # Sort by timestamp
            messages = sorted(messages, key=lambda m: m.timestamp)
            # Apply offset and limit
            messages = messages[offset:]
            if limit is not None:
                messages = messages[:limit]
            return list(messages)

    def delete_message(self, message_id: str, session_id: str) -> bool:
        """Delete a message from in-memory storage.

        Args:
            message_id: The ID of the message to delete.
            session_id: The session the message belongs to.

        Returns:
            True if deleted, False if not found.
        """
        with self._lock:
            messages = self._messages.get(session_id, [])
            for i, msg in enumerate(messages):
                if msg.id == message_id:
                    messages.pop(i)
                    return True
            return False

    def search_messages(
        self,
        session_id: str,
        keyword: str,
        limit: Optional[int] = None,
    ) -> List[Message]:
        """Search messages by keyword in in-memory storage.

        Args:
            session_id: The session to search in.
            keyword: The keyword to search for (case-insensitive).
            limit: Maximum number of results.

        Returns:
            A list of matching Message objects.
        """
        with self._lock:
            messages = self._messages.get(session_id, [])
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
        with self._lock:
            return list(self._sessions.values())

    def save_session_meta(self, session_id: str, meta: Dict[str, Any]) -> None:
        """Save session metadata to in-memory storage.

        Args:
            session_id: The session ID.
            meta: The metadata dictionary.
        """
        with self._lock:
            self._sessions[session_id] = meta

    def load_session_meta(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load session metadata from in-memory storage.

        Args:
            session_id: The session ID.

        Returns:
            The metadata dictionary, or None if not found.
        """
        with self._lock:
            return self._sessions.get(session_id)

    def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its messages.

        Args:
            session_id: The session ID to delete.

        Returns:
            True if the session was deleted, False if not found.
        """
        with self._lock:
            existed = session_id in self._sessions or session_id in self._messages
            if session_id in self._sessions:
                del self._sessions[session_id]
            if session_id in self._messages:
                del self._messages[session_id]
            return existed

    def close(self) -> None:
        """Release resources. No-op for in-memory backend."""
        pass
