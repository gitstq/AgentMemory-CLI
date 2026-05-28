"""CLI entry point for AgentMemory.

Provides a command-line interface using argparse for managing AI agent
memory sessions, messages, context windows, and exports.
"""

from __future__ import annotations

import argparse
import sys
from typing import Optional

from agentmemory import __version__
from agentmemory.core.memory import MemoryStore
from agentmemory.storage.base import StorageBackend
from agentmemory.storage.json_backend import JSONBackend
from agentmemory.storage.memory_backend import MemoryBackend
from agentmemory.storage.sqlite_backend import SQLiteBackend


def _create_backend(
    backend_type: str, store_path: str
) -> StorageBackend:
    """Create a storage backend based on the specified type.

    Args:
        backend_type: The backend type ('sqlite', 'json', or 'memory').
        store_path: The path for file-based backends.

    Returns:
        A StorageBackend instance.

    Raises:
        ValueError: If the backend type is not supported.
    """
    if backend_type == "sqlite":
        db_path = store_path if store_path.endswith(".db") else f"{store_path}/memory.db"
        return SQLiteBackend(store_path=db_path)
    elif backend_type == "json":
        return JSONBackend(store_path=store_path)
    elif backend_type == "memory":
        return MemoryBackend(store_path=store_path)
    else:
        raise ValueError(
            f"Unsupported backend '{backend_type}'. "
            f"Choose from: sqlite, json, memory"
        )


def _get_store(args: argparse.Namespace) -> MemoryStore:
    """Create a MemoryStore from parsed CLI arguments.

    Args:
        args: The parsed argparse namespace.

    Returns:
        A configured MemoryStore instance.
    """
    backend = _create_backend(args.backend, args.store_path)
    return MemoryStore(backend=backend)


def cmd_session_create(args: argparse.Namespace) -> None:
    """Handle 'session create' command.

    Args:
        args: Parsed CLI arguments with 'name' attribute.
    """
    store = _get_store(args)
    try:
        session = store.session_manager.create_session(
            name=args.name, tags=args.tags
        )
        print(f"Session created successfully.")
        print(f"  ID:   {session['session_id']}")
        print(f"  Name: {session['name']}")
        print(f"  Tags: {', '.join(session['tags']) or 'None'}")
    finally:
        store.close()


def cmd_session_list(args: argparse.Namespace) -> None:
    """Handle 'session list' command.

    Args:
        args: Parsed CLI arguments.
    """
    store = _get_store(args)
    try:
        sessions = store.session_manager.list_sessions()
        if not sessions:
            print("No sessions found.")
            return

        active_id = store.session_manager.active_session_id
        print(f"{'ID':<40} {'Name':<20} {'Messages':>8}  Active")
        print("-" * 80)
        for s in sessions:
            sid = s.get("session_id", "")
            name = s.get("name", "Untitled")
            count = s.get("message_count", 0)
            is_active = " *" if sid == active_id else ""
            print(f"{sid:<40} {name:<20} {count:>8}{is_active}")
    finally:
        store.close()


def cmd_session_delete(args: argparse.Namespace) -> None:
    """Handle 'session delete' command.

    Args:
        args: Parsed CLI arguments with 'id' attribute.
    """
    store = _get_store(args)
    try:
        success = store.session_manager.delete_session(args.id)
        if success:
            print(f"Session '{args.id}' deleted successfully.")
        else:
            print(f"Session '{args.id}' not found.")
    finally:
        store.close()


def cmd_session_switch(args: argparse.Namespace) -> None:
    """Handle 'session switch' command.

    Args:
        args: Parsed CLI arguments with 'id' attribute.
    """
    store = _get_store(args)
    try:
        success = store.session_manager.switch_session(args.id)
        if success:
            session = store.session_manager.get_active_session()
            name = session.get("name", "Unknown") if session else "Unknown"
            print(f"Switched to session: {name} ({args.id})")
        else:
            print(f"Session '{args.id}' not found.")
    finally:
        store.close()


def cmd_msg_add(args: argparse.Namespace) -> None:
    """Handle 'msg add' command.

    Args:
        args: Parsed CLI arguments with 'role' and 'content' attributes.
    """
    store = _get_store(args)
    try:
        message = store.add_message(role=args.role, content=args.content)
        print(f"Message added successfully.")
        print(f"  ID:   {message.id}")
        print(f"  Role: {message.role}")
        print(f"  Time: {message.timestamp}")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        store.close()


def cmd_msg_list(args: argparse.Namespace) -> None:
    """Handle 'msg list' command.

    Args:
        args: Parsed CLI arguments with optional 'session' and 'limit'.
    """
    store = _get_store(args)
    try:
        messages = store.get_messages(
            session_id=args.session,
            limit=args.limit,
            role=args.role,
        )
        if not messages:
            print("No messages found.")
            return

        for i, msg in enumerate(messages, 1):
            role_tag = msg.role.upper()
            content_preview = (
                msg.content[:100] + "..."
                if len(msg.content) > 100
                else msg.content
            )
            print(f"  {i}. [{role_tag}] {content_preview}")
            print(f"     ID: {msg.id}  Time: {msg.timestamp[:19]}")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        store.close()


def cmd_msg_search(args: argparse.Namespace) -> None:
    """Handle 'msg search' command.

    Args:
        args: Parsed CLI arguments with 'keyword' attribute.
    """
    store = _get_store(args)
    try:
        messages = store.search_messages(
            keyword=args.keyword,
            session_id=args.session,
            limit=args.limit,
        )
        if not messages:
            print(f"No messages found matching '{args.keyword}'.")
            return

        print(f"Found {len(messages)} message(s):")
        for i, msg in enumerate(messages, 1):
            content_preview = (
                msg.content[:100] + "..."
                if len(msg.content) > 100
                else msg.content
            )
            print(f"  {i}. [{msg.role.upper()}] {content_preview}")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        store.close()


def cmd_msg_delete(args: argparse.Namespace) -> None:
    """Handle 'msg delete' command.

    Args:
        args: Parsed CLI arguments with 'id' attribute.
    """
    store = _get_store(args)
    try:
        success = store.delete_message(message_id=args.id)
        if success:
            print(f"Message '{args.id}' deleted successfully.")
        else:
            print(f"Message '{args.id}' not found.")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        store.close()


def cmd_context(args: argparse.Namespace) -> None:
    """Handle 'context' command.

    Args:
        args: Parsed CLI arguments with optional 'limit'.
    """
    store = _get_store(args)
    try:
        ctx = store.get_context_window(limit=args.limit)
        print(f"Total messages in session: {ctx['total_messages']}")
        print()

        if ctx["summary"]:
            print("=== Session Summary ===")
            print(ctx["summary"])
            print()

        print(f"=== Recent {len(ctx['messages'])} Messages ===")
        for i, msg in enumerate(ctx["messages"], 1):
            role_tag = msg.role.upper()
            print(f"  {i}. [{role_tag}] {msg.content[:120]}")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        store.close()


def cmd_export(args: argparse.Namespace) -> None:
    """Handle 'export' command.

    Args:
        args: Parsed CLI arguments with 'format', optional 'session' and
            'output'.
    """
    from agentmemory.export.exporter import Exporter

    store = _get_store(args)
    try:
        session_id = args.session
        session_meta = None

        if session_id:
            session_meta = store.session_manager.get_session(session_id)
            messages = store.get_messages(session_id=session_id)
        else:
            active = store.session_manager.get_active_session()
            if active:
                session_id = active["session_id"]
                session_meta = active
                messages = store.get_messages(session_id=session_id)
            else:
                print("No session specified and no active session.", file=sys.stderr)
                sys.exit(1)

        result = Exporter.export(
            fmt=args.format,
            messages=messages,
            session_meta=session_meta,
        )

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(result)
            print(f"Exported {len(messages)} messages to {args.output}")
        else:
            print(result)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        store.close()


def cmd_dashboard(args: argparse.Namespace) -> None:
    """Handle 'dashboard' command.

    Args:
        args: Parsed CLI arguments.
    """
    from agentmemory.tui.dashboard import Dashboard

    store = _get_store(args)
    try:
        dashboard = Dashboard(store)
        dashboard.run()
    finally:
        store.close()


def cmd_summary(args: argparse.Namespace) -> None:
    """Handle 'summary' command.

    Args:
        args: Parsed CLI arguments.
    """
    store = _get_store(args)
    try:
        summary = store.get_summary()
        if summary:
            print(store.summarizer.get_summary_text(summary))
        else:
            print("No summary available for the current session.")
            print("(Summaries are auto-generated when message count exceeds threshold.)")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        store.close()


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the CLI.

    Returns:
        The configured ArgumentParser.
    """
    parser = argparse.ArgumentParser(
        prog="agentmemory",
        description="AgentMemory-CLI: Lightweight stateful memory management "
        "engine for AI Agents.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    # Global options
    parser.add_argument(
        "--backend",
        choices=["sqlite", "json", "memory"],
        default="memory",
        help="Storage backend to use (default: memory)",
    )
    parser.add_argument(
        "--store-path",
        default="./agentmemory_data",
        help="Path for file-based storage (default: ./agentmemory_data)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- session subcommands ---
    session_parser = subparsers.add_parser("session", help="Manage sessions")
    session_sub = session_parser.add_subparsers(dest="subcommand")

    # session create
    create_p = session_sub.add_parser("create", help="Create a new session")
    create_p.add_argument("name", help="Session name")
    create_p.add_argument(
        "--tags", nargs="*", default=[], help="Tags for the session"
    )
    create_p.set_defaults(func=cmd_session_create)

    # session list
    list_p = session_sub.add_parser("list", help="List all sessions")
    list_p.set_defaults(func=cmd_session_list)

    # session delete
    delete_p = session_sub.add_parser("delete", help="Delete a session")
    delete_p.add_argument("id", help="Session ID to delete")
    delete_p.set_defaults(func=cmd_session_delete)

    # session switch
    switch_p = session_sub.add_parser("switch", help="Switch active session")
    switch_p.add_argument("id", help="Session ID to switch to")
    switch_p.set_defaults(func=cmd_session_switch)

    # --- msg subcommands ---
    msg_parser = subparsers.add_parser("msg", help="Manage messages")
    msg_sub = msg_parser.add_subparsers(dest="subcommand")

    # msg add
    add_p = msg_sub.add_parser("add", help="Add a message")
    add_p.add_argument("role", help="Message role (user/assistant/system)")
    add_p.add_argument("content", help="Message content")
    add_p.set_defaults(func=cmd_msg_add)

    # msg list
    msg_list_p = msg_sub.add_parser("list", help="List messages")
    msg_list_p.add_argument(
        "--session", default=None, help="Session ID (default: active session)"
    )
    msg_list_p.add_argument(
        "--limit", type=int, default=None, help="Max messages to show"
    )
    msg_list_p.add_argument(
        "--role", default=None, help="Filter by role (user/assistant/system)"
    )
    msg_list_p.set_defaults(func=cmd_msg_list)

    # msg search
    search_p = msg_sub.add_parser("search", help="Search messages")
    search_p.add_argument("keyword", help="Search keyword")
    search_p.add_argument(
        "--session", default=None, help="Session ID (default: active session)"
    )
    search_p.add_argument(
        "--limit", type=int, default=None, help="Max results"
    )
    search_p.set_defaults(func=cmd_msg_search)

    # msg delete
    msg_del_p = msg_sub.add_parser("delete", help="Delete a message")
    msg_del_p.add_argument("id", help="Message ID to delete")
    msg_del_p.set_defaults(func=cmd_msg_delete)

    # --- context ---
    ctx_p = subparsers.add_parser("context", help="Get context window")
    ctx_p.add_argument(
        "--limit", type=int, default=10, help="Number of recent messages"
    )
    ctx_p.set_defaults(func=cmd_context)

    # --- export ---
    export_p = subparsers.add_parser("export", help="Export session data")
    export_p.add_argument(
        "format", choices=["json", "markdown", "csv"], help="Export format"
    )
    export_p.add_argument(
        "--session", default=None, help="Session ID (default: active session)"
    )
    export_p.add_argument(
        "--output", default=None, help="Output file path (default: stdout)"
    )
    export_p.set_defaults(func=cmd_export)

    # --- dashboard ---
    dash_p = subparsers.add_parser("dashboard", help="Launch TUI dashboard")
    dash_p.set_defaults(func=cmd_dashboard)

    # --- summary ---
    sum_p = subparsers.add_parser("summary", help="View session summary")
    sum_p.set_defaults(func=cmd_summary)

    return parser


def main(argv: Optional[list[str]] = None) -> None:
    """Main entry point for the AgentMemory CLI.

    Args:
        argv: Command-line arguments. If None, uses sys.argv[1:].
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
