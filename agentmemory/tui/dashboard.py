"""TUI Dashboard for AgentMemory using the rich library.

Provides an interactive terminal dashboard for viewing session information,
recent messages, and session statistics.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from agentmemory.core.memory import MemoryStore


class Dashboard:
    """Interactive TUI dashboard for AgentMemory.

    Displays current session information, recent messages, and session
    statistics using the rich library for rich terminal output.

    Attributes:
        store: The MemoryStore instance to display data from.
    """

    def __init__(self, store: MemoryStore) -> None:
        """Initialize the Dashboard.

        Args:
            store: The MemoryStore instance to use for data.
        """
        self.store = store

    def run(self) -> None:
        """Run the interactive TUI dashboard.

        Displays session overview and recent messages. Supports keyboard
        interaction: 'q' to quit, 'n' to add a new message, 's' to switch
        sessions.
        """
        try:
            from rich.console import Console
            from rich.panel import Panel
            from rich.table import Table
            from rich.text import Text
            from rich.prompt import Prompt
        except ImportError:
            print(
                "Error: The 'rich' library is required for the TUI dashboard.\n"
                "Install it with: pip install rich>=13.0.0"
            )
            return

        console = Console()

        while True:
            console.clear()
            self._render_dashboard(console)

            console.print()
            console.print(
                "[bold cyan]Actions:[/bold cyan] "
                "[green]n[/green]=new message  "
                "[green]s[/green]=switch session  "
                "[green]q[/green]=quit"
            )

            action = Prompt.ask(
                "[bold]Enter action[/bold]",
                choices=["n", "s", "q"],
                default="q",
            )

            if action == "q":
                console.print("[yellow]Goodbye![/yellow]")
                break
            elif action == "n":
                self._add_message_interactive(console)
            elif action == "s":
                self._switch_session_interactive(console)

    def _render_dashboard(self, console: object) -> None:
        """Render the dashboard view.

        Args:
            console: The rich Console instance.
        """
        from rich.panel import Panel
        from rich.table import Table
        from rich.text import Text

        # Session info
        active = self.store.session_manager.get_active_session()
        if active:
            session_info = (
                f"[bold]Session:[/bold] {active.get('name', 'Untitled')}\n"
                f"[bold]ID:[/bold] {active.get('session_id', 'N/A')[:8]}...\n"
                f"[bold]Messages:[/bold] {active.get('message_count', 0)}\n"
                f"[bold]Tags:[/bold] {', '.join(active.get('tags', [])) or 'None'}"
            )
        else:
            session_info = "[yellow]No active session. Use 's' to switch.[/yellow]"

        console.print(Panel(session_info, title="Session Info", border_style="blue"))

        # Recent messages
        try:
            messages = self.store.get_messages(limit=10)
        except ValueError:
            messages = []

        if messages:
            table = Table(title="Recent Messages", show_lines=True)
            table.add_column("#", style="dim", width=4)
            table.add_column("Role", style="bold", width=10)
            table.add_column("Content", width=60)
            table.add_column("Time", style="dim", width=20)

            for i, msg in enumerate(messages, 1):
                content = msg.content[:80] + ("..." if len(msg.content) > 80 else "")
                time_str = msg.timestamp[:19] if msg.timestamp else "N/A"
                role_style = {
                    "user": "green",
                    "assistant": "cyan",
                    "system": "yellow",
                }.get(msg.role, "white")

                table.add_row(
                    str(i),
                    f"[{role_style}]{msg.role}[/{role_style}]",
                    content,
                    time_str,
                )

            console.print(table)
        else:
            console.print("[dim]No messages to display.[/dim]")

        # Session statistics
        sessions = self.store.session_manager.list_sessions()
        total_messages = sum(
            s.get("message_count", 0) for s in sessions
        )
        stats_text = (
            f"[bold]Total Sessions:[/bold] {len(sessions)}  |  "
            f"[bold]Total Messages:[/bold] {total_messages}"
        )
        console.print(Panel(stats_text, title="Statistics", border_style="green"))

    def _add_message_interactive(self, console: object) -> None:
        """Interactively add a new message.

        Args:
            console: The rich Console instance.
        """
        from rich.prompt import Prompt

        console.print()
        role = Prompt.ask(
            "[bold]Role[/bold]",
            choices=["user", "assistant", "system"],
            default="user",
        )
        content = Prompt.ask("[bold]Content[/bold]")
        if content.strip():
            try:
                self.store.add_message(role=role, content=content)
                console.print("[green]Message added successfully.[/green]")
            except ValueError as e:
                console.print(f"[red]Error: {e}[/red]")
        else:
            console.print("[yellow]Empty content, message not added.[/yellow]")

    def _switch_session_interactive(self, console: object) -> None:
        """Interactively switch to a different session.

        Args:
            console: The rich Console instance.
        """
        from rich.prompt import Prompt
        from rich.table import Table

        sessions = self.store.session_manager.list_sessions()
        if not sessions:
            console.print("[yellow]No sessions available.[/yellow]")
            return

        table = Table(title="Available Sessions")
        table.add_column("#", style="dim", width=4)
        table.add_column("Name", style="bold")
        table.add_column("ID", style="dim")
        table.add_column("Messages", justify="right")

        for i, s in enumerate(sessions, 1):
            table.add_row(
                str(i),
                s.get("name", "Untitled"),
                s.get("session_id", "")[:8] + "...",
                str(s.get("message_count", 0)),
            )

        console.print(table)

        choice = Prompt.ask(
            "[bold]Select session number[/bold]",
            default="1",
        )
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(sessions):
                sid = sessions[idx]["session_id"]
                self.store.session_manager.switch_session(sid)
                console.print(
                    f"[green]Switched to session: "
                    f"{sessions[idx].get('name', 'Untitled')}[/green]"
                )
            else:
                console.print("[red]Invalid session number.[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number.[/red]")
