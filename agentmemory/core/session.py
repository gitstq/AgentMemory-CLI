"""Session management for AgentMemory.

Manages the lifecycle of conversation sessions, including creation,
deletion, listing, switching, and searching.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from agentmemory.storage.base import StorageBackend


class SessionManager:
    """Manages conversation sessions with independent message storage.

    Each session has its own message history and metadata including
    creation time, last update time, message count, and tags.

    Attributes:
        backend: The storage backend used for persistence.
        active_session_id: The currently active session ID, or None.
    """

    def __init__(self, backend: StorageBackend) -> None:
        """Initialize the SessionManager.

        Args:
            backend: The storage backend for session persistence.
        """
        self.backend = backend
        self.active_session_id: Optional[str] = None

    def create_session(
        self, name: str, tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a new session.

        Args:
            name: A human-readable name for the session.
            tags: Optional list of tags for categorization.

        Returns:
            A dictionary containing the session metadata.
        """
        session_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        meta: Dict[str, Any] = {
            "session_id": session_id,
            "name": name,
            "created_at": now,
            "updated_at": now,
            "message_count": 0,
            "tags": tags or [],
        }
        self.backend.save_session_meta(session_id, meta)
        return meta

    def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its messages.

        Args:
            session_id: The ID of the session to delete.

        Returns:
            True if the session was deleted, False if not found.
        """
        result = self.backend.delete_session(session_id)
        if result and self.active_session_id == session_id:
            self.active_session_id = None
        return result

    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all sessions.

        Returns:
            A list of session metadata dictionaries, sorted by
            last update time descending.
        """
        sessions = self.backend.get_session_list()
        sessions.sort(key=lambda s: s.get("updated_at", ""), reverse=True)
        return sessions

    def switch_session(self, session_id: str) -> bool:
        """Switch the active session.

        Args:
            session_id: The ID of the session to switch to.

        Returns:
            True if the switch was successful, False if session not found.
        """
        meta = self.backend.load_session_meta(session_id)
        if meta is None:
            return False
        self.active_session_id = session_id
        return True

    def get_active_session(self) -> Optional[Dict[str, Any]]:
        """Get the currently active session's metadata.

        Returns:
            The active session's metadata, or None if no active session.
        """
        if self.active_session_id is None:
            return None
        return self.backend.load_session_meta(self.active_session_id)

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific session.

        Args:
            session_id: The session ID to look up.

        Returns:
            The session metadata, or None if not found.
        """
        return self.backend.load_session_meta(session_id)

    def search_sessions(
        self, keyword: Optional[str] = None, tag: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search sessions by name keyword or tag.

        Args:
            keyword: Optional keyword to search in session names
                (case-insensitive, fuzzy match).
            tag: Optional tag to filter sessions by.

        Returns:
            A list of matching session metadata dictionaries.
        """
        sessions = self.list_sessions()
        results: List[Dict[str, Any]] = []

        for session in sessions:
            match = True
            if keyword:
                name = session.get("name", "").lower()
                if keyword.lower() not in name:
                    match = False
            if tag:
                tags = session.get("tags", [])
                if tag not in tags:
                    match = False
            if match:
                results.append(session)

        return results

    def update_session_meta(
        self, session_id: str, updates: Dict[str, Any]
    ) -> bool:
        """Update metadata fields for a session.

        Args:
            session_id: The session ID to update.
            updates: A dictionary of fields to update. Supported keys:
                name, tags.

        Returns:
            True if the update was successful, False if session not found.
        """
        meta = self.backend.load_session_meta(session_id)
        if meta is None:
            return False

        for key, value in updates.items():
            if key in ("name", "tags"):
                meta[key] = value

        meta["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.backend.save_session_meta(session_id, meta)
        return True

    def increment_message_count(self, session_id: str) -> None:
        """Increment the message count for a session.

        Args:
            session_id: The session ID to update.
        """
        meta = self.backend.load_session_meta(session_id)
        if meta is not None:
            meta["message_count"] = meta.get("message_count", 0) + 1
            meta["updated_at"] = datetime.now(timezone.utc).isoformat()
            self.backend.save_session_meta(session_id, meta)
