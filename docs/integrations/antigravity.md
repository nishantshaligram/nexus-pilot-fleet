# Google Antigravity Integration

NexusPilot Fleet integrates with Google Antigravity as a first-class orchestration plugin.

---

## Automatic Installation

```bash
npx nexus-pilot-fleet install --agent antigravity
```
Or via batch launcher:
```cmd
install-fleet.bat -Antigravity
```

This copies the plugin bundle to:
`~/.gemini/config/plugins/nexus-pilot-fleet/`

---

## Bundled Skills

| Skill | Directory | Description |
| :--- | :--- | :--- |
| `swarm-orchestrator` | `skills/swarm-orchestrator/` | Multi-agent mission planning, DAG decomposition, and Two-Key review dispatch. |
| `mission-control` | `skills/mission-control/` | Real-time progress monitoring, squad health, and blackboard querying. |

---

## Agent Directives

Fleet injects behavioral guardrails from `rules/AGENTS.md` ensuring all participating agents:
- Strictly isolate code in designated worktrees (`fleet/worker-<id>-<task>`).
- Enforce Two-Key approval before code merges into the integration pipeline.
- Broadcast shared contracts to the blackboard.
