"""Storage backends for AgentMemory."""

from agentmemory.storage.base import StorageBackend
from agentmemory.storage.json_backend import JSONBackend
from agentmemory.storage.memory_backend import MemoryBackend

try:
    from agentmemory.storage.sqlite_backend import SQLiteBackend
except ImportError:
    # sqlite3 is part of the standard library, so this should never happen
    SQLiteBackend = None  # type: ignore[assignment,misc]

__all__ = [
    "StorageBackend",
    "JSONBackend",
    "MemoryBackend",
    "SQLiteBackend",
]
