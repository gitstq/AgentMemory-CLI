"""Multi-format exporter for AgentMemory sessions.

Supports exporting session data to JSON, Markdown, and CSV formats.
"""

from __future__ import annotations

import csv
import io
import json
from typing import Any, Dict, List, Optional

from agentmemory.core.message import Message


class Exporter:
    """Exports session messages and metadata to multiple formats.

    Supported formats: JSON, Markdown, CSV.
    """

    @staticmethod
    def export_json(
        messages: List[Message],
        session_meta: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Export messages to JSON format.

        Args:
            messages: The list of messages to export.
            session_meta: Optional session metadata to include.

        Returns:
            A JSON string containing the exported data.
        """
        data: Dict[str, Any] = {
            "session": session_meta or {},
            "messages": [msg.to_dict() for msg in messages],
            "exported_count": len(messages),
        }
        return json.dumps(data, ensure_ascii=False, indent=2)

    @staticmethod
    def export_markdown(
        messages: List[Message],
        session_meta: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Export messages to Markdown format.

        Includes a header section with session metadata if provided.

        Args:
            messages: The list of messages to export.
            session_meta: Optional session metadata to include.

        Returns:
            A Markdown string containing the exported data.
        """
        lines: List[str] = []

        # Session metadata header
        if session_meta:
            lines.append(f"# Session: {session_meta.get('name', 'Untitled')}")
            lines.append("")
            lines.append(f"- **Session ID**: `{session_meta.get('session_id', 'N/A')}`")
            lines.append(f"- **Created**: {session_meta.get('created_at', 'N/A')}")
            lines.append(f"- **Updated**: {session_meta.get('updated_at', 'N/A')}")
            lines.append(f"- **Messages**: {session_meta.get('message_count', len(messages))}")
            tags = session_meta.get("tags", [])
            if tags:
                lines.append(f"- **Tags**: {', '.join(tags)}")
            lines.append("")
            lines.append("---")
            lines.append("")

        # Messages
        lines.append("## Messages")
        lines.append("")

        if not messages:
            lines.append("*No messages in this session.*")
        else:
            for i, msg in enumerate(messages, 1):
                role_label = msg.role.capitalize()
                lines.append(f"### {i}. [{role_label}]")
                lines.append("")
                lines.append(f"> {msg.content}")
                lines.append("")
                lines.append(f"*{msg.timestamp}*")
                if msg.metadata:
                    meta_str = ", ".join(
                        f"{k}: {v}" for k, v in msg.metadata.items()
                    )
                    lines.append(f"*Metadata: {meta_str}*")
                lines.append("")

        return "\n".join(lines)

    @staticmethod
    def export_csv(
        messages: List[Message],
        session_meta: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Export messages to CSV format.

        Args:
            messages: The list of messages to export.
            session_meta: Optional session metadata (not included in CSV).

        Returns:
            A CSV string containing the exported data.
        """
        output = io.StringIO()
        writer = csv.writer(output)

        # Header row
        writer.writerow(["id", "role", "content", "timestamp", "session_id"])

        # Data rows
        for msg in messages:
            writer.writerow([
                msg.id,
                msg.role,
                msg.content,
                msg.timestamp,
                msg.session_id,
            ])

        return output.getvalue()

    @classmethod
    def export(
        cls,
        fmt: str,
        messages: List[Message],
        session_meta: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Export messages to the specified format.

        Args:
            fmt: The export format ('json', 'markdown', or 'csv').
            messages: The list of messages to export.
            session_meta: Optional session metadata.

        Returns:
            The exported data as a string.

        Raises:
            ValueError: If the format is not supported.
        """
        exporters = {
            "json": cls.export_json,
            "markdown": cls.export_markdown,
            "md": cls.export_markdown,
            "csv": cls.export_csv,
        }

        fmt_lower = fmt.lower()
        if fmt_lower not in exporters:
            supported = ", ".join(sorted(set(exporters.keys())))
            raise ValueError(
                f"Unsupported format '{fmt}'. Supported: {supported}"
            )

        return exporters[fmt_lower](messages, session_meta)
