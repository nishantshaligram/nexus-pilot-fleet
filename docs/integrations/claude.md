# Claude Integration (Code CLI & Desktop)

NexusPilot Fleet integrates with both **Claude Code CLI** and the **Claude Desktop App**.

---

## 1-Command Setup

```bash
npx nexus-pilot-fleet install --agent claude
```
Or via Windows batch:
```cmd
install-fleet.bat -Claude
```

This configures:
* **Claude Code CLI:** `~/.claude.json`
* **Claude Desktop App:** `%APPDATA%\Claude\claude_desktop_config.json`

---

## Manual MCP Configuration

In your Claude MCP settings:

```json
{
  "mcpServers": {
    "nexus-pilot-fleet": {
      "command": "npx",
      "args": ["-y", "nexus-pilot-fleet"]
    }
  }
}
```
Reload Claude to access Fleet's mission orchestration tools.
