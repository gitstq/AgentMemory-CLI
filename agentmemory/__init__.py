"""AgentMemory - Lightweight stateful memory management engine for AI Agents."""

__version__ = "1.0.0"

from agentmemory.core.memory import MemoryStore
from agentmemory.core.session import SessionManager
from agentmemory.core.message import Message, Role
from agentmemory.core.summary import AutoSummarizer

__all__ = [
    "__version__",
    "MemoryStore",
    "SessionManager",
    "Message",
    "Role",
    "AutoSummarizer",
]
