"""Abstract base class for storage backends."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from agentmemory.core.message import Message


class StorageBackend(ABC):
    """Abstract base class defining the storage interface.

    All storage backends must implement these methods to provide a
    consistent interface for message and session persistence.
    """

    @abstractmethod
    def save_message(self, message: Message) -> None:
        """Persist a single message to storage.

        Args:
            message: The Message object to save.
        """
        ...

    @abstractmethod
    def load_messages(
        self,
        session_id: str,
        limit: Optional[int] = None,
        offset: int = 0,
        role: Optional[str] = None,
    ) -> List[Message]:
        """Load messages for a given session.

        Args:
            session_id: The session to load messages from.
            limit: Maximum number of messages to return. None for all.
            offset: Number of messages to skip from the beginning.
            role: Optional role filter (user/assistant/system).

        Returns:
            A list of Message objects, ordered by timestamp ascending.
        """
        ...

    @abstractmethod
    def delete_message(self, message_id: str, session_id: str) -> bool:
        """Delete a message by its ID.

        Args:
            message_id: The ID of the message to delete.
            session_id: The session the message belongs to.

        Returns:
            True if the message was deleted, False if not found.
        """
        ...

    @abstractmethod
    def search_messages(
        self,
        session_id: str,
        keyword: str,
        limit: Optional[int] = None,
    ) -> List[Message]:
        """Search messages by keyword within a session.

        Args:
            session_id: The session to search in.
            keyword: The keyword to search for (case-insensitive).
            limit: Maximum number of results. None for all.

        Returns:
            A list of matching Message objects.
        """
        ...

    @abstractmethod
    def get_session_list(self) -> List[Dict[str, Any]]:
        """Get a list of all sessions with their metadata.

        Returns:
            A list of dictionaries, each containing session metadata.
        """
        ...

    @abstractmethod
    def save_session_meta(self, session_id: str, meta: Dict[str, Any]) -> None:
        """Save or update session metadata.

        Args:
            session_id: The session ID.
            meta: A dictionary of metadata to store.
        """
        ...

    @abstractmethod
    def load_session_meta(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load metadata for a specific session.

        Args:
            session_id: The session ID.

        Returns:
            A dictionary of session metadata, or None if not found.
        """
        ...

    @abstractmethod
    def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its messages.

        Args:
            session_id: The session ID to delete.

        Returns:
            True if the session was deleted, False if not found.
        """
        ...

    @abstractmethod
    def close(self) -> None:
        """Close any open connections or resources."""
        ...
