# Quickstart Guide

Launch your first multi-agent mission with NexusPilot Fleet in under 2 minutes.

---

## 1. Verify Fleet Status
Ask your agent to verify Fleet subsystem health:
> *"Run check_fleet_health to verify Git worktrees and swarm database."*

Fleet returns:
```json
{
  "status": "online",
  "engine": "NexusPilot Fleet",
  "version": "1.0.0",
  "is_git_repo": true,
  "database_path": ".../fleet_bus.db",
  "active_worktrees_count": 0
}
```

---

## 2. Initialize a Multi-Agent Mission
Instruct your agent with a high-level software engineering goal:
> *"Initialize a fleet mission to refactor all REST endpoints to Fastify and add unit tests."*

Fleet creates the mission and provisions the worker squad:
* **`worker-author-1`:** Lead Author Coder (Model: `gemini-1.5-flash`)
* **`worker-reviewer`:** Security & Architecture Auditor (Model: `gemini-1.5-pro`)
* **`worker-verifier`:** Sandbox Test Runner (Model: `gemini-2.0-flash`)

---

## 3. Autonomous DAG Task Decomposition
Fleet decomposes your goal into topologically sorted sub-tasks:
1. `T1`: Architecture Contract & Type Definitions *(No dependencies)*
2. `T2`: Core Auth Endpoints *(Depends on T1)*
3. `T3`: Billing & Invoice Endpoints *(Depends on T1, runs in parallel with T2)*
4. `T4`: Integration Test Suite *(Depends on T2 and T3)*
5. `T5`: OpenAPI Specs & Documentation *(Depends on T4)*

---

## 4. Zero-Collision Worktree Execution & Two-Key Consensus
Fleet automatically dispatches ready tasks to isolated disk copies:
* `worker-author-1` receives worktree `.fleet/worktrees/worker-author-1` on branch `fleet/worker-author-1-T1`.
* When work is finished, the worker calls `submit_task_for_review`.
* The **Reviewer Agent** audits the diff and grants **Key 1**.
* The **Verifier Agent** runs the sandbox test suite and grants **Key 2**.
* Once both keys are acquired, Fleet merges the branch into `fleet/integration` and cleans up the worktree.
