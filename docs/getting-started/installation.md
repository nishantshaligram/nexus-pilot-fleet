# Installation Guide

NexusPilot Fleet provides multiple zero-friction installation pathways depending on your preferred workflow.

---

## 1. Zero-Install NPX Execution

You can integrate Fleet directly into any AI agent without cloning the repo:

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

---

## 2. 1-Command CLI Installer

To install plugins, skills, and configuration into your local AI agents:

```bash
# Interactive selection
npx nexus-pilot-fleet install

# Or target specific agents directly
npx nexus-pilot-fleet install --agent antigravity
npx nexus-pilot-fleet install --agent claude
npx nexus-pilot-fleet install --ide cursor
npx nexus-pilot-fleet install --ide windsurf
```

---

## 3. Windows 1-Click Interactive Batch Installer

If working from source on Windows:
```cmd
:: Launch interactive installer
install-fleet.bat

:: Or pass targeted environment flags
install-fleet.bat -Antigravity
install-fleet.bat -Claude
install-fleet.bat -Target "Antigravity, Cursor"
```

---

## 4. Diagnostic Health Check

Verify your Git worktree capability, Python environment, and SQLite database at any time:

```bash
npx nexus-pilot-fleet doctor
```
