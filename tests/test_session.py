"""Tests for the SessionManager."""

import unittest

from agentmemory.core.session import SessionManager
from agentmemory.storage.memory_backend import MemoryBackend


class TestSessionManager(unittest.TestCase):
    """Test cases for the SessionManager class."""

    def setUp(self) -> None:
        """Set up a SessionManager with MemoryBackend for each test."""
        self.backend = MemoryBackend()
        self.manager = SessionManager(self.backend)

    def tearDown(self) -> None:
        """Clean up after each test."""
        self.backend.close()

    def test_create_session(self) -> None:
        """Test creating a new session."""
        session = self.manager.create_session("Test Session")
        self.assertIsNotNone(session["session_id"])
        self.assertEqual(session["name"], "Test Session")
        self.assertEqual(session["message_count"], 0)
        self.assertEqual(session["tags"], [])
        self.assertIsNotNone(session["created_at"])
        self.assertIsNotNone(session["updated_at"])

    def test_create_session_with_tags(self) -> None:
        """Test creating a session with tags."""
        session = self.manager.create_session(
            "Tagged Session", tags=["test", "demo"]
        )
        self.assertEqual(session["tags"], ["test", "demo"])

    def test_delete_session(self) -> None:
        """Test deleting a session."""
        session = self.manager.create_session("To Delete")
        sid = session["session_id"]

        success = self.manager.delete_session(sid)
        self.assertTrue(success)

        # Verify session is gone
        meta = self.manager.get_session(sid)
        self.assertIsNone(meta)

    def test_delete_nonexistent_session(self) -> None:
        """Test deleting a non-existent session returns False."""
        success = self.manager.delete_session("nonexistent-id")
        self.assertFalse(success)

    def test_delete_active_session_clears_active(self) -> None:
        """Test that deleting the active session clears active_session_id."""
        session = self.manager.create_session("Active")
        sid = session["session_id"]
        self.manager.switch_session(sid)
        self.assertEqual(self.manager.active_session_id, sid)

        self.manager.delete_session(sid)
        self.assertIsNone(self.manager.active_session_id)

    def test_list_sessions(self) -> None:
        """Test listing all sessions."""
        self.manager.create_session("Session 1")
        self.manager.create_session("Session 2")
        self.manager.create_session("Session 3")

        sessions = self.manager.list_sessions()
        self.assertEqual(len(sessions), 3)

    def test_list_sessions_sorted_by_updated_at(self) -> None:
        """Test that sessions are sorted by updated_at descending."""
        s1 = self.manager.create_session("First")
        s2 = self.manager.create_session("Second")

        sessions = self.manager.list_sessions()
        # Most recently created should be first
        self.assertEqual(sessions[0]["session_id"], s2["session_id"])
        self.assertEqual(sessions[1]["session_id"], s1["session_id"])

    def test_switch_session(self) -> None:
        """Test switching active session."""
        s1 = self.manager.create_session("Session 1")
        s2 = self.manager.create_session("Session 2")

        success = self.manager.switch_session(s1["session_id"])
        self.assertTrue(success)
        self.assertEqual(self.manager.active_session_id, s1["session_id"])

        success = self.manager.switch_session(s2["session_id"])
        self.assertTrue(success)
        self.assertEqual(self.manager.active_session_id, s2["session_id"])

    def test_switch_nonexistent_session(self) -> None:
        """Test switching to a non-existent session returns False."""
        success = self.manager.switch_session("nonexistent-id")
        self.assertFalse(success)
        self.assertIsNone(self.manager.active_session_id)

    def test_get_active_session(self) -> None:
        """Test getting the active session metadata."""
        self.assertIsNone(self.manager.get_active_session())

        session = self.manager.create_session("Active")
        self.manager.switch_session(session["session_id"])
        active = self.manager.get_active_session()
        self.assertIsNotNone(active)
        self.assertEqual(active["name"], "Active")

    def test_get_session(self) -> None:
        """Test getting a specific session by ID."""
        session = self.manager.create_session("Target")
        retrieved = self.manager.get_session(session["session_id"])
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["name"], "Target")

    def test_get_nonexistent_session(self) -> None:
        """Test getting a non-existent session returns None."""
        result = self.manager.get_session("nonexistent-id")
        self.assertIsNone(result)

    def test_search_sessions_by_keyword(self) -> None:
        """Test searching sessions by name keyword."""
        self.manager.create_session("Python Development")
        self.manager.create_session("Java Development")
        self.manager.create_session("Meeting Notes")

        results = self.manager.search_sessions(keyword="development")
        self.assertEqual(len(results), 2)

    def test_search_sessions_by_tag(self) -> None:
        """Test searching sessions by tag."""
        self.manager.create_session("Session 1", tags=["python", "dev"])
        self.manager.create_session("Session 2", tags=["java", "dev"])
        self.manager.create_session("Session 3", tags=["meeting"])

        results = self.manager.search_sessions(tag="dev")
        self.assertEqual(len(results), 2)

    def test_search_sessions_combined(self) -> None:
        """Test searching sessions with both keyword and tag."""
        self.manager.create_session("Python Dev", tags=["python"])
        self.manager.create_session("Java Dev", tags=["java"])
        self.manager.create_session("Python Notes", tags=["notes"])

        results = self.manager.search_sessions(keyword="python", tag="python")
        self.assertEqual(len(results), 1)

    def test_update_session_meta(self) -> None:
        """Test updating session metadata."""
        session = self.manager.create_session("Original")
        sid = session["session_id"]

        success = self.manager.update_session_meta(sid, {"name": "Updated"})
        self.assertTrue(success)

        updated = self.manager.get_session(sid)
        self.assertEqual(updated["name"], "Updated")

    def test_update_session_tags(self) -> None:
        """Test updating session tags."""
        session = self.manager.create_session("Tagged")
        sid = session["session_id"]

        success = self.manager.update_session_meta(
            sid, {"tags": ["new", "tags"]}
        )
        self.assertTrue(success)

        updated = self.manager.get_session(sid)
        self.assertEqual(updated["tags"], ["new", "tags"])

    def test_update_nonexistent_session(self) -> None:
        """Test updating a non-existent session returns False."""
        success = self.manager.update_session_meta(
            "nonexistent-id", {"name": "Test"}
        )
        self.assertFalse(success)

    def test_increment_message_count(self) -> None:
        """Test incrementing the message count."""
        session = self.manager.create_session("Counter")
        sid = session["session_id"]

        self.manager.increment_message_count(sid)
        self.manager.increment_message_count(sid)
        self.manager.increment_message_count(sid)

        updated = self.manager.get_session(sid)
        self.assertEqual(updated["message_count"], 3)


if __name__ == "__main__":
    unittest.main()
