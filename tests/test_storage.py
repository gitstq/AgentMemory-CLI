"""Tests for all storage backends."""

import os
import tempfile
import unittest
from typing import Type

from agentmemory.core.message import Message
from agentmemory.storage.base import StorageBackend
from agentmemory.storage.json_backend import JSONBackend
from agentmemory.storage.memory_backend import MemoryBackend
from agentmemory.storage.sqlite_backend import SQLiteBackend


class StorageBackendTestMixin:
    """Mixin with common tests for all storage backends.

    Subclasses must set self.backend_class and self.backend_kwargs in setUp.
    """

    backend_class: Type[StorageBackend]
    backend_kwargs: dict

    def setUp(self) -> None:
        """Set up the backend instance."""
        self.backend = self.backend_class(**self.backend_kwargs)

    def tearDown(self) -> None:
        """Clean up the backend."""
        self.backend.close()

    def _create_message(
        self,
        role: str = "user",
        content: str = "Test message",
        session_id: str = "test-session",
    ) -> Message:
        """Helper to create a test message."""
        return Message(role=role, content=content, session_id=session_id)

    def test_save_and_load_messages(self) -> None:
        """Test saving and loading messages."""
        msg = self._create_message()
        self.backend.save_message(msg)

        messages = self.backend.load_messages("test-session")
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].id, msg.id)
        self.assertEqual(messages[0].content, "Test message")

    def test_load_messages_with_limit(self) -> None:
        """Test loading messages with a limit."""
        for i in range(5):
            msg = self._create_message(content=f"Message {i}")
            self.backend.save_message(msg)

        messages = self.backend.load_messages("test-session", limit=3)
        self.assertEqual(len(messages), 3)

    def test_load_messages_with_offset(self) -> None:
        """Test loading messages with an offset."""
        for i in range(5):
            msg = self._create_message(content=f"Message {i}")
            self.backend.save_message(msg)

        messages = self.backend.load_messages("test-session", offset=3)
        self.assertEqual(len(messages), 2)

    def test_load_messages_with_role_filter(self) -> None:
        """Test loading messages filtered by role."""
        self.backend.save_message(self._create_message(role="user"))
        self.backend.save_message(self._create_message(role="assistant"))
        self.backend.save_message(self._create_message(role="user"))

        messages = self.backend.load_messages("test-session", role="user")
        self.assertEqual(len(messages), 2)

    def test_load_empty_session(self) -> None:
        """Test loading messages from an empty/non-existent session."""
        messages = self.backend.load_messages("nonexistent")
        self.assertEqual(len(messages), 0)

    def test_delete_message(self) -> None:
        """Test deleting a message."""
        msg = self._create_message()
        self.backend.save_message(msg)

        success = self.backend.delete_message(msg.id, "test-session")
        self.assertTrue(success)

        messages = self.backend.load_messages("test-session")
        self.assertEqual(len(messages), 0)

    def test_delete_nonexistent_message(self) -> None:
        """Test deleting a non-existent message returns False."""
        success = self.backend.delete_message("fake-id", "test-session")
        self.assertFalse(success)

    def test_search_messages(self) -> None:
        """Test searching messages by keyword."""
        self.backend.save_message(
            self._create_message(content="Python programming is fun")
        )
        self.backend.save_message(
            self._create_message(content="Java programming is nice")
        )
        self.backend.save_message(
            self._create_message(content="Hello world")
        )

        results = self.backend.search_messages("test-session", "python")
        self.assertEqual(len(results), 1)
        self.assertIn("Python", results[0].content)

    def test_search_with_limit(self) -> None:
        """Test searching messages with a limit."""
        for i in range(5):
            self.backend.save_message(
                self._create_message(content=f"Python test {i}")
            )

        results = self.backend.search_messages("test-session", "python", limit=2)
        self.assertEqual(len(results), 2)

    def test_save_and_load_session_meta(self) -> None:
        """Test saving and loading session metadata."""
        meta = {
            "session_id": "s1",
            "name": "Test Session",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
            "message_count": 0,
            "tags": ["test"],
        }
        self.backend.save_session_meta("s1", meta)

        loaded = self.backend.load_session_meta("s1")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["name"], "Test Session")
        self.assertEqual(loaded["tags"], ["test"])

    def test_load_nonexistent_session_meta(self) -> None:
        """Test loading metadata for a non-existent session."""
        meta = self.backend.load_session_meta("nonexistent")
        self.assertIsNone(meta)

    def test_get_session_list(self) -> None:
        """Test getting the list of all sessions."""
        self.backend.save_session_meta("s1", {"name": "Session 1"})
        self.backend.save_session_meta("s2", {"name": "Session 2"})

        sessions = self.backend.get_session_list()
        self.assertEqual(len(sessions), 2)

    def test_delete_session(self) -> None:
        """Test deleting a session."""
        self.backend.save_session_meta("s1", {"name": "To Delete"})
        msg = self._create_message(session_id="s1")
        self.backend.save_message(msg)

        success = self.backend.delete_session("s1")
        self.assertTrue(success)

        meta = self.backend.load_session_meta("s1")
        self.assertIsNone(meta)

    def test_delete_nonexistent_session(self) -> None:
        """Test deleting a non-existent session returns False."""
        success = self.backend.delete_session("nonexistent")
        self.assertFalse(success)

    def test_multiple_sessions_isolated(self) -> None:
        """Test that messages from different sessions are isolated."""
        msg1 = self._create_message(
            content="Session 1 message", session_id="s1"
        )
        msg2 = self._create_message(
            content="Session 2 message", session_id="s2"
        )
        self.backend.save_message(msg1)
        self.backend.save_message(msg2)

        s1_msgs = self.backend.load_messages("s1")
        s2_msgs = self.backend.load_messages("s2")

        self.assertEqual(len(s1_msgs), 1)
        self.assertEqual(len(s2_msgs), 1)
        self.assertEqual(s1_msgs[0].content, "Session 1 message")
        self.assertEqual(s2_msgs[0].content, "Session 2 message")


class TestMemoryBackend(StorageBackendTestMixin, unittest.TestCase):
    """Tests for the MemoryBackend."""

    def setUp(self) -> None:
        """Set up MemoryBackend."""
        self.backend_class = MemoryBackend
        self.backend_kwargs = {"store_path": ""}
        super().setUp()


class TestJSONBackend(StorageBackendTestMixin, unittest.TestCase):
    """Tests for the JSONBackend."""

    def setUp(self) -> None:
        """Set up JSONBackend with a temporary directory."""
        self.tmpdir = tempfile.mkdtemp()
        self.backend_class = JSONBackend
        self.backend_kwargs = {"store_path": self.tmpdir}
        super().setUp()

    def tearDown(self) -> None:
        """Clean up temporary directory."""
        super().tearDown()
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_atomic_write(self) -> None:
        """Test that atomic write creates the expected file."""
        msg = self._create_message()
        self.backend.save_message(msg)

        # Check that the session file exists
        session_files = [
            f for f in os.listdir(self.tmpdir)
            if f.startswith("session_") and f.endswith(".json")
        ]
        self.assertEqual(len(session_files), 1)

    def test_session_file_persists(self) -> None:
        """Test that data persists across backend instances."""
        msg = self._create_message(content="Persistent data")
        self.backend.save_message(msg)
        self.backend.close()

        # Create a new backend pointing to the same directory
        new_backend = JSONBackend(store_path=self.tmpdir)
        messages = new_backend.load_messages("test-session")
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].content, "Persistent data")
        new_backend.close()


class TestSQLiteBackend(StorageBackendTestMixin, unittest.TestCase):
    """Tests for the SQLiteBackend."""

    def setUp(self) -> None:
        """Set up SQLiteBackend with a temporary database."""
        self.tmpdir = tempfile.mkdtemp()
        db_path = os.path.join(self.tmpdir, "test.db")
        self.backend_class = SQLiteBackend
        self.backend_kwargs = {"store_path": db_path}
        super().setUp()

    def tearDown(self) -> None:
        """Clean up temporary directory."""
        super().tearDown()
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_database_file_created(self) -> None:
        """Test that the database file is created."""
        db_path = os.path.join(self.tmpdir, "test.db")
        self.assertTrue(os.path.exists(db_path))

    def test_data_persists_across_instances(self) -> None:
        """Test that data persists across backend instances."""
        msg = self._create_message(content="Persistent SQLite data")
        self.backend.save_message(msg)
        self.backend.close()

        db_path = os.path.join(self.tmpdir, "test.db")
        new_backend = SQLiteBackend(store_path=db_path)
        messages = new_backend.load_messages("test-session")
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].content, "Persistent SQLite data")
        new_backend.close()

    def test_fts5_search(self) -> None:
        """Test FTS5 full-text search."""
        self.backend.save_message(
            self._create_message(content="The quick brown fox jumps")
        )
        self.backend.save_message(
            self._create_message(content="A lazy dog sleeps")
        )

        results = self.backend.search_messages("test-session", "quick")
        self.assertEqual(len(results), 1)
        self.assertIn("quick", results[0].content.lower())


if __name__ == "__main__":
    unittest.main()
