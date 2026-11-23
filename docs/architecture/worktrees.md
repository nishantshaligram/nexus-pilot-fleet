# Architecture: Git Worktree Multiplexer

The Worktree Multiplexer eliminates file-lock contention and merge conflicts by giving each worker agent an isolated physical directory on disk.

---

## 1. The Worktree Lifecycle

```mermaid
sequenceDiagram
    participant Orchestrator as Fleet Orchestrator
    participant Git as Git Engine
    participant Worker as Worker Agent (Author)
    participant Arbitrator as Merge Arbitrator

    Orchestrator->>Git: git worktree add -b fleet/worker-01-T1 .fleet/worktrees/worker-01 main
    Git-->>Orchestrator: Worktree provisioned on disk
    Orchestrator->>Worker: Dispatches task in .fleet/worktrees/worker-01
    Worker->>Worker: Edits files, formats, compiles independently
    Worker-->>Orchestrator: Work complete (git commit)
    Orchestrator->>Arbitrator: Stages merge into fleet/integration
    Arbitrator->>Git: Clean merge verified
    Orchestrator->>Git: git worktree remove .fleet/worktrees/worker-01 --force
    Git-->>Orchestrator: Worktree pruned cleanly
```

---

## 2. Disk Isolation Guarantees

* **Zero File Contention:** 10 workers can run `npm install`, compile TypeScript, or run formatters concurrently without file locks or index race conditions.
* **Zero Accidental Commits to Main:** All work occurs on isolated branches (`fleet/worker-<id>-<task>`).
* **Clean Teardown:** Once merged, `prune_worktree` removes temporary directories and runs `git worktree prune`.
