"""Tests for the export functionality."""

import unittest

from agentmemory.core.message import Message
from agentmemory.export.exporter import Exporter


class TestExporter(unittest.TestCase):
    """Test cases for the Exporter class."""

    def setUp(self) -> None:
        """Set up test messages and session metadata."""
        self.messages = [
            Message(
                id="msg-1",
                role="user",
                content="Hello, how are you?",
                timestamp="2024-01-01T10:00:00",
                session_id="s1",
            ),
            Message(
                id="msg-2",
                role="assistant",
                content="I'm doing well, thank you! How can I help?",
                timestamp="2024-01-01T10:01:00",
                session_id="s1",
            ),
            Message(
                id="msg-3",
                role="user",
                content="Tell me about Python programming.",
                timestamp="2024-01-01T10:02:00",
                session_id="s1",
                metadata={"topic": "python"},
            ),
        ]
        self.session_meta = {
            "session_id": "s1",
            "name": "Test Session",
            "created_at": "2024-01-01T10:00:00",
            "updated_at": "2024-01-01T10:02:00",
            "message_count": 3,
            "tags": ["test", "demo"],
        }

    def test_export_json(self) -> None:
        """Test JSON export format."""
        result = Exporter.export_json(self.messages, self.session_meta)

        import json
        data = json.loads(result)

        self.assertEqual(data["session"]["name"], "Test Session")
        self.assertEqual(data["exported_count"], 3)
        self.assertEqual(len(data["messages"]), 3)
        self.assertEqual(data["messages"][0]["role"], "user")
        self.assertEqual(data["messages"][1]["content"], "I'm doing well, thank you! How can I help?")

    def test_export_json_without_meta(self) -> None:
        """Test JSON export without session metadata."""
        result = Exporter.export_json(self.messages)

        import json
        data = json.loads(result)

        self.assertEqual(data["session"], {})
        self.assertEqual(data["exported_count"], 3)

    def test_export_markdown(self) -> None:
        """Test Markdown export format."""
        result = Exporter.export_markdown(self.messages, self.session_meta)

        self.assertIn("# Session: Test Session", result)
        self.assertIn("Session ID", result)
        self.assertIn("Created", result)
        self.assertIn("Tags", result)
        self.assertIn("test, demo", result)
        self.assertIn("## Messages", result)
        self.assertIn("[User]", result)
        self.assertIn("[Assistant]", result)
        self.assertIn("Hello, how are you?", result)

    def test_export_markdown_empty_messages(self) -> None:
        """Test Markdown export with no messages."""
        result = Exporter.export_markdown([], self.session_meta)
        self.assertIn("No messages in this session", result)

    def test_export_markdown_without_meta(self) -> None:
        """Test Markdown export without session metadata."""
        result = Exporter.export_markdown(self.messages)
        self.assertIn("## Messages", result)
        self.assertNotIn("# Session:", result)

    def test_export_csv(self) -> None:
        """Test CSV export format."""
        result = Exporter.export_csv(self.messages)

        lines = result.strip().split("\n")
        self.assertEqual(len(lines), 4)  # header + 3 messages
        self.assertIn("id,role,content,timestamp,session_id", lines[0])
        self.assertIn("user", lines[1])
        self.assertIn("assistant", lines[2])
        self.assertIn("Python", lines[3])

    def test_export_csv_empty(self) -> None:
        """Test CSV export with no messages."""
        result = Exporter.export_csv([])
        lines = result.strip().split("\n")
        self.assertEqual(len(lines), 1)  # header only

    def test_export_generic_json(self) -> None:
        """Test generic export method with JSON format."""
        result = Exporter.export("json", self.messages, self.session_meta)
        import json
        data = json.loads(result)
        self.assertEqual(data["exported_count"], 3)

    def test_export_generic_markdown(self) -> None:
        """Test generic export method with Markdown format."""
        result = Exporter.export("markdown", self.messages, self.session_meta)
        self.assertIn("# Session:", result)

    def test_export_generic_md_alias(self) -> None:
        """Test that 'md' is an alias for 'markdown'."""
        result_md = Exporter.export("md", self.messages, self.session_meta)
        result_markdown = Exporter.export("markdown", self.messages, self.session_meta)
        self.assertEqual(result_md, result_markdown)

    def test_export_generic_csv(self) -> None:
        """Test generic export method with CSV format."""
        result = Exporter.export("csv", self.messages)
        self.assertIn("id,role,content", result)

    def test_export_unsupported_format(self) -> None:
        """Test that unsupported format raises ValueError."""
        with self.assertRaises(ValueError) as ctx:
            Exporter.export("xml", self.messages)
        self.assertIn("Unsupported format", str(ctx.exception))

    def test_export_long_content_truncation_in_markdown(self) -> None:
        """Test that long content is handled in Markdown export."""
        long_msg = Message(
            id="msg-long",
            role="user",
            content="A" * 500,
            session_id="s1",
        )
        result = Exporter.export_markdown([long_msg])
        # Content should be included in full (blockquote)
        self.assertIn("A" * 500, result)


if __name__ == "__main__":
    unittest.main()
