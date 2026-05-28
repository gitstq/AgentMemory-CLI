# AgentMemory-CLI

A lightweight terminal AI Agent stateful memory management engine.

## Installation

```bash
pip install -e .
```

## Usage

```bash
# Create a session
agentmemory session create "My Session"

# Switch to a session
agentmemory session switch <session-id>

# Add messages
agentmemory msg add user "Hello!"
agentmemory msg add assistant "Hi there!"

# List messages
agentmemory msg list

# Search messages
agentmemory msg search "keyword"

# Get context window
agentmemory context --limit 10

# View summary
agentmemory summary

# Export session
agentmemory export json --output session.json
agentmemory export markdown --output session.md
agentmemory export csv --output session.csv

# Launch TUI dashboard (requires rich)
agentmemory dashboard
```

## Storage Backends

- `--backend memory` (default): In-memory storage, no persistence
- `--backend json`: JSON file-based storage
- `--backend sqlite`: SQLite database with FTS5 full-text search

## License

MIT
