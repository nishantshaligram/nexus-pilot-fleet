"""
NexusPilot Fleet - Cross-Platform MCP Config Updater
Safely updates Claude, Antigravity, Cursor, and Windsurf MCP configuration files
without shell quoting issues or PowerShell object model errors.
"""

import sys
import os
import json
import argparse


def update_mcp_config(config_path: str, server_name: str, command: str, script_path: str, description: str):
    config_path = os.path.expanduser(os.path.expandvars(config_path))
    os.makedirs(os.path.dirname(os.path.abspath(config_path)), exist_ok=True)

    data = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
        except Exception as e:
            sys.stderr.write(f"Warning: Existing config {config_path} could not be parsed: {e}\n")
            data = {}

    if not isinstance(data, dict):
        data = {}

    servers = data.setdefault("mcpServers", {})
    if not isinstance(servers, dict):
        servers = {}
        data["mcpServers"] = servers

    servers[server_name] = {
        "command": command,
        "args": [script_path],
        "description": description
    }

    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Successfully configured: {config_path}")
    except PermissionError:
        sys.stderr.write(f"Permission denied writing to {config_path}. Run installer with elevated/user permissions.\n")
    except Exception as e:
        sys.stderr.write(f"Error writing to {config_path}: {e}\n")


def main():
    parser = argparse.ArgumentParser(description="Update MCP configuration file for NexusPilot Fleet")
    parser.add_argument("config_path", help="Path to MCP JSON config file")
    parser.add_argument("server_name", help="Name of MCP server")
    parser.add_argument("--command", required=True, help="Binary to run (e.g., python)")
    parser.add_argument("--script", required=True, help="Path to server script")
    parser.add_argument("--description", default="NexusPilot Fleet MCP Server", help="Server description")

    args = parser.parse_args()
    update_mcp_config(
        config_path=args.config_path,
        server_name=args.server_name,
        command=args.command,
        script_path=args.script,
        description=args.description
    )


if __name__ == "__main__":
    main()
