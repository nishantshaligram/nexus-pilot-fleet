# Security Policy

## Responsible Disclosure

The NexusPilot team takes security, source code protection, and system integrity seriously. Because NexusPilot Fleet provisions isolated git worktrees, executes parallel subprocesses, and manages automated branch merges, we enforce strict guardrails:

- **Zero Main Branch Contention:** All multi-agent execution is isolated in dedicated git worktree directories (`.fleet/worktrees/worker-<id>`) on intermediate feature branches (`fleet/worker-...`). Direct commits or pushes to production/main branches are prevented.
- **Two-Key Consensus Gate:** Code requires independent sign-offs from both the Reviewer Agent (Architecture & Security) and Verifier Agent (Sandbox Build & Tests) before entering the integration pipeline.
- **Local-First Event Store:** All mission states and blackboard facts are stored locally in an embedded SQLite database (`.fleet/fleet_bus.db`). Zero external telemetry exfiltration.

If you discover a vulnerability or safety bypass in NexusPilot Fleet:
- **Email:** nishant.shaligram@gmail.com
- We aim to acknowledge receipt within 48 hours and provide a remediation timeline.
