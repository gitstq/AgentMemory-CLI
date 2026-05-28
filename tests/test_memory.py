"""Tests for the MemoryStore core functionality."""

import unittest
from datetime import datetime, timezone

from agentmemory.core.memory import MemoryStore
from agentmemory.core.message import Message, Role
from agentmemory.storage.memory_backend import MemoryBackend


class TestMemoryStore(unittest.TestCase):
    """Test cases for the MemoryStore class."""

    def setUp(self) -> None:
        """Set up a MemoryStore with MemoryBackend for each test."""
        self.backend = MemoryBackend()
        self.store = MemoryStore(backend=self.backend, summary_threshold=20)

    def tearDown(self) -> None:
        """Clean up after each test."""
        self.store.close()

    def test_add_message_without_session_raises(self) -> None:
        """Test that adding a message without a session raises ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.store.add_message(role="user", content="hello")
        self.assertIn("No session", str(ctx.exception))

    def test_add_and_get_messages(self) -> None:
        """Test adding and retrieving messages."""
        session = self.store.session_manager.create_session("test")
        sid = session["session_id"]
        self.store.session_manager.switch_session(sid)

        self.store.add_message(role="user", content="Hello!")
        self.store.add_message(role="assistant", content="Hi there!")

        messages = self.store.get_messages()
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0].role, "user")
        self.assertEqual(messages[0].content, "Hello!")
        self.assertEqual(messages[1].role, "assistant")
        self.assertEqual(messages[1].content, "Hi there!")

    def test_add_message_returns_message(self) -> None:
        """Test that add_message returns a Message with proper fields."""
        session = self.store.session_manager.create_session("test")
        sid = session["session_id"]
        self.store.session_manager.switch_session(sid)

        msg = self.store.add_message(role="user", content="Test content")
        self.assertIsInstance(msg, Message)
        self.assertEqual(msg.role, "user")
        self.assertEqual(msg.content, "Test content")
        self.assertEqual(msg.session_id, sid)
        self.assertIsNotNone(msg.id)
        self.assertIsNotNone(msg.timestamp)

    def test_get_messages_with_limit(self) -> None:
        """Test retrieving messages with a limit."""
        session = self.store.session_manager.create_session("test")
        sid = session["session_id"]
        self.store.session_manager.switch_session(sid)

        for i in range(5):
            self.store.add_message(role="user", content=f"Message {i}")

        messages = self.store.get_messages(limit=3)
        self.assertEqual(len(messages), 3)

    def test_get_messages_with_offset(self) -> None:
        """Test retrieving messages with an offset."""
        session = self.store.session_manager.create_session("test")
        sid = session["session_id"]
        self.store.session_manager.switch_session(sid)

        for i in range(5):
            self.store.add_message(role="user", content=f"Message {i}")

        messages = self.store.get_messages(offset=3)
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0].content, "Message 3")

    def test_get_messages_with_role_filter(self) -> None:
        """Test retrieving messages filtered by role."""
        session = self.store.session_manager.create_session("test")
        sid = session["session_id"]
        self.store.session_manager.switch_session(sid)

        self.store.add_message(role="user", content="User msg 1")
        self.store.add_message(role="assistant", content="Assistant msg")
        self.store.add_message(role="user", content="User msg 2")

        user_msgs = self.store.get_messages(role="user")
        self.assertEqual(len(user_msgs), 2)
        self.assertTrue(all(m.role == "user" for m in user_msgs))

    def test_search_messages(self) -> None:
        """Test searching messages by keyword."""
        session = self.store.session_manager.create_session("test")
        sid = session["session_id"]
        self.store.session_manager.switch_session(sid)

        self.store.add_message(role="user", content="I love Python programming")
        self.store.add_message(role="assistant", content="Python is great!")
        self.store.add_message(role="user", content="Hello world")

        results = self.store.search_messages("python")
        self.assertEqual(len(results), 2)

    def test_delete_message(self) -> None:
        """Test deleting a message."""
        session = self.store.session_manager.create_session("test")
        sid = session["session_id"]
        self.store.session_manager.switch_session(sid)

        msg = self.store.add_message(role="user", content="To be deleted")
        self.assertEqual(len(self.store.get_messages()), 1)

        success = self.store.delete_message(msg.id)
        self.assertTrue(success)
        self.assertEqual(len(self.store.get_messages()), 0)

    def test_delete_nonexistent_message(self) -> None:
        """Test deleting a non-existent message returns False."""
        session = self.store.session_manager.create_session("test")
        sid = session["session_id"]
        self.store.session_manager.switch_session(sid)

        success = self.store.delete_message("nonexistent-id")
        self.assertFalse(success)

    def test_get_context_window(self) -> None:
        """Test getting the context window."""
        session = self.store.session_manager.create_session("test")
        sid = session["session_id"]
        self.store.session_manager.switch_session(sid)

        for i in range(15):
            self.store.add_message(role="user", content=f"Message {i}")

        ctx = self.store.get_context_window(limit=5)
        self.assertEqual(ctx["total_messages"], 15)
        self.assertEqual(len(ctx["messages"]), 5)
        self.assertEqual(ctx["messages"][-1].content, "Message 14")

    def test_auto_summarization(self) -> None:
        """Test that auto-summarization triggers at threshold."""
        # Create store with low threshold for testing
        backend = MemoryBackend()
        store = MemoryStore(backend=backend, summary_threshold=5)

        session = store.session_manager.create_session("test")
        sid = session["session_id"]
        store.session_manager.switch_session(sid)

        # Add messages up to threshold
        for i in range(5):
            store.add_message(role="user", content=f"Python programming topic {i}")

        # Should have triggered summarization
        summary = store.get_summary()
        self.assertIsNotNone(summary)
        self.assertIn("keywords", summary)
        self.assertGreater(len(summary["keywords"]), 0)

        store.close()

    def test_get_context_window_without_session_raises(self) -> None:
        """Test that get_context_window without session raises ValueError."""
        with self.assertRaises(ValueError):
            self.store.get_context_window()

    def test_search_without_session_raises(self) -> None:
        """Test that search without session raises ValueError."""
        with self.assertRaises(ValueError):
            self.store.search_messages("test")

    def test_explicit_session_id(self) -> None:
        """Test using explicit session_id instead of active session."""
        session = self.store.session_manager.create_session("test")
        sid = session["session_id"]

        # Do NOT switch to the session, use explicit ID
        self.store.add_message(
            role="user", content="Hello", session_id=sid
        )
        messages = self.store.get_messages(session_id=sid)
        self.assertEqual(len(messages), 1)

    def test_add_message_with_metadata(self) -> None:
        """Test adding a message with custom metadata."""
        session = self.store.session_manager.create_session("test")
        sid = session["session_id"]
        self.store.session_manager.switch_session(sid)

        msg = self.store.add_message(
            role="user",
            content="Hello",
            metadata={"source": "test", "priority": 1},
        )
        self.assertEqual(msg.metadata["source"], "test")
        self.assertEqual(msg.metadata["priority"], 1)


if __name__ == "__main__":
    unittest.main()
