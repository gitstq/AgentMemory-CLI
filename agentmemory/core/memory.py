"""MemoryStore - Core memory storage engine for AgentMemory.

Provides a unified interface for all memory operations including adding,
retrieving, searching, and deleting messages. Supports automatic
summarization when session message count exceeds a configurable threshold.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from agentmemory.core.message import Message, Role
from agentmemory.core.session import SessionManager
from agentmemory.core.summary import AutoSummarizer
from agentmemory.storage.base import StorageBackend


class MemoryStore:
    """Core memory storage engine.

    Manages all memory operations through a pluggable storage backend.
    Provides automatic summarization of old messages when a session
    exceeds the configured message threshold.

    Attributes:
        backend: The storage backend for persistence.
        session_manager: The session manager for session lifecycle.
        summarizer: The auto-summarizer for compressing old messages.
        summary_threshold: Number of messages before auto-summarization.
    """

    def __init__(
        self,
        backend: StorageBackend,
        summary_threshold: int = 20,
    ) -> None:
        """Initialize the MemoryStore.

        Args:
            backend: The storage backend to use.
            summary_threshold: Number of messages before auto-summarization
                is triggered for a session.
        """
        self.backend = backend
        self.session_manager = SessionManager(backend)
        self.summarizer = AutoSummarizer(threshold=summary_threshold)
        self.summary_threshold = summary_threshold
        self._session_summaries: Dict[str, Dict[str, Any]] = {}

    def add_message(
        self,
        role: str,
        content: str,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Message:
        """Add a new message to a session.

        Args:
            role: The role of the message sender (user/assistant/system).
            content: The text content of the message.
            session_id: The session ID. If None, uses the active session.
            metadata: Optional key-value metadata.

        Returns:
            The created Message object.

        Raises:
            ValueError: If no session is specified and no active session exists.
        """
        Role.from_string(role)  # Validate role

        if session_id is None:
            session_id = self.session_manager.active_session_id
        if session_id is None:
            raise ValueError(
                "No session specified and no active session. "
                "Create or switch to a session first."
            )

        message = Message(
            role=role,
            content=content,
            session_id=session_id,
            metadata=metadata or {},
        )

        self.backend.save_message(message)
        self.session_manager.increment_message_count(session_id)

        # Check if auto-summarization should be triggered
        messages = self.backend.load_messages(session_id)
        if self.summarizer.should_summarize(len(messages)):
            self._auto_summarize(session_id, messages)

        return message

    def get_messages(
        self,
        session_id: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0,
        role: Optional[str] = None,
    ) -> List[Message]:
        """Get messages from a session.

        Args:
            session_id: The session ID. If None, uses the active session.
            limit: Maximum number of messages to return.
            offset: Number of messages to skip.
            role: Optional role filter.

        Returns:
            A list of Message objects.

        Raises:
            ValueError: If no session is specified and no active session exists.
        """
        if session_id is None:
            session_id = self.session_manager.active_session_id
        if session_id is None:
            raise ValueError(
                "No session specified and no active session. "
                "Create or switch to a session first."
            )

        return self.backend.load_messages(
            session_id, limit=limit, offset=offset, role=role
        )

    def search_messages(
        self,
        keyword: str,
        session_id: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Message]:
        """Search messages by keyword.

        Args:
            keyword: The keyword to search for (case-insensitive).
            session_id: The session ID. If None, uses the active session.
            limit: Maximum number of results.

        Returns:
            A list of matching Message objects.

        Raises:
            ValueError: If no session is specified and no active session exists.
        """
        if session_id is None:
            session_id = self.session_manager.active_session_id
        if session_id is None:
            raise ValueError(
                "No session specified and no active session. "
                "Create or switch to a session first."
            )

        return self.backend.search_messages(session_id, keyword, limit=limit)

    def delete_message(
        self, message_id: str, session_id: Optional[str] = None
    ) -> bool:
        """Delete a message by ID.

        Args:
            message_id: The ID of the message to delete.
            session_id: The session ID. If None, uses the active session.

        Returns:
            True if the message was deleted, False if not found.

        Raises:
            ValueError: If no session is specified and no active session exists.
        """
        if session_id is None:
            session_id = self.session_manager.active_session_id
        if session_id is None:
            raise ValueError(
                "No session specified and no active session. "
                "Create or switch to a session first."
            )

        return self.backend.delete_message(message_id, session_id)

    def get_context_window(
        self,
        session_id: Optional[str] = None,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """Get the context window for a session.

        Returns the most recent messages plus any auto-generated summary
        of older messages.

        Args:
            session_id: The session ID. If None, uses the active session.
            limit: Maximum number of recent messages to include.

        Returns:
            A dictionary containing:
                - summary: The session summary text (if available).
                - messages: List of recent Message objects.
                - total_messages: Total message count in the session.

        Raises:
            ValueError: If no session is specified and no active session exists.
        """
        if session_id is None:
            session_id = self.session_manager.active_session_id
        if session_id is None:
            raise ValueError(
                "No session specified and no active session. "
                "Create or switch to a session first."
            )

        all_messages = self.backend.load_messages(session_id)
        total = len(all_messages)

        # Get summary if available
        summary = self._session_summaries.get(session_id)
        summary_text = ""
        if summary:
            summary_text = self.summarizer.get_summary_text(summary)

        # Get recent messages
        recent = all_messages[-limit:] if total > limit else all_messages

        return {
            "summary": summary_text,
            "messages": recent,
            "total_messages": total,
        }

    def get_summary(
        self, session_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get the current summary for a session.

        Args:
            session_id: The session ID. If None, uses the active session.

        Returns:
            The summary dictionary, or None if no summary exists.

        Raises:
            ValueError: If no session is specified and no active session exists.
        """
        if session_id is None:
            session_id = self.session_manager.active_session_id
        if session_id is None:
            raise ValueError(
                "No session specified and no active session. "
                "Create or switch to a session first."
            )

        return self._session_summaries.get(session_id)

    def _auto_summarize(
        self, session_id: str, messages: List[Message]
    ) -> None:
        """Perform auto-summarization on older messages.

        Summarizes all but the most recent messages and stores the summary.

        Args:
            session_id: The session ID.
            messages: All messages in the session.
        """
        if len(messages) < self.summary_threshold:
            return

        # Summarize older messages (keep recent ones out of summary)
        keep_count = self.summary_threshold // 2
        older_messages = messages[:-keep_count] if keep_count > 0 else messages

        if older_messages:
            summary = self.summarizer.summarize(older_messages)
            self._session_summaries[session_id] = summary

    def close(self) -> None:
        """Close the storage backend and release resources."""
        self.backend.close()
