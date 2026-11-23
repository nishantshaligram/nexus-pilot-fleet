# Cursor IDE & Windsurf Integration

NexusPilot Fleet provides full MCP support for **Cursor IDE** and **Codeium Windsurf**.

---

## 1-Command Setup

```bash
# For Cursor IDE
npx nexus-pilot-fleet install --ide cursor

# For Windsurf
npx nexus-pilot-fleet install --ide windsurf
```

This configures:
* **Cursor:** `~/.cursor/mcp.json`
* **Windsurf:** `~/.codeium/windsurf/mcp_config.json`

---

## Manual Configuration

In Cursor or Windsurf MCP settings:

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
Reload your editor window to activate the tools.
