"""Message data model for AgentMemory."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict


class Role(str, Enum):
    """Enumeration of possible message roles."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

    @classmethod
    def values(cls) -> list[str]:
        """Return all valid role values as strings."""
        return [member.value for member in cls]

    @classmethod
    def from_string(cls, value: str) -> Role:
        """Parse a role from string, case-insensitive.

        Args:
            value: The role string to parse.

        Returns:
            The corresponding Role enum member.

        Raises:
            ValueError: If the value is not a valid role.
        """
        try:
            return cls(value.lower())
        except ValueError:
            valid = ", ".join(cls.values())
            raise ValueError(f"Invalid role '{value}'. Must be one of: {valid}")


@dataclass
class Message:
    """Represents a single message in a conversation.

    Attributes:
        id: Unique identifier for the message (UUID4 by default).
        role: The role of the message sender (user/assistant/system).
        content: The text content of the message.
        timestamp: When the message was created (UTC by default).
        metadata: Optional key-value metadata attached to the message.
        session_id: The ID of the session this message belongs to.
    """

    role: str
    content: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: Dict[str, Any] = field(default_factory=dict)
    session_id: str = ""

    def __post_init__(self) -> None:
        """Validate role after initialization."""
        Role.from_string(self.role)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the message to a dictionary.

        Returns:
            A dictionary representation of the message.
        """
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
            "session_id": self.session_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Message:
        """Deserialize a message from a dictionary.

        Args:
            data: A dictionary containing message data.

        Returns:
            A Message instance.

        Raises:
            KeyError: If required fields are missing.
        """
        return cls(
            id=data["id"],
            role=data["role"],
            content=data["content"],
            timestamp=data.get(
                "timestamp", datetime.now(timezone.utc).isoformat()
            ),
            metadata=data.get("metadata", {}),
            session_id=data.get("session_id", ""),
        )

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        return f"[{self.role}] {self.content[:80]}{'...' if len(self.content) > 80 else ''}"
