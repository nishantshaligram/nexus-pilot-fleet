# MCP Tool Catalog

NexusPilot Fleet exposes 13 tools across Orchestration, Consensus, Worktree Multiplexing, and Event Bus subsystems.

---

## 🛸 Orchestration Tools

### `create_mission`
Initializes a new multi-agent mission with a high-level goal and provisions initial worker squad.
* **Parameters:**
  * `goal` (string, required): The software engineering directive.
  * `base_branch` (string, optional, default: `"main"`)
  * `mission_id` (string, optional)

### `decompose_goal`
Breaks a goal into topologically sorted DAG nodes with dependency mapping.
* **Parameters:**
  * `mission_id` (string, required)
  * `goal` (string, optional)

### `dispatch_ready_tasks`
Scans DAG for ready tasks whose dependencies are satisfied, provisions an isolated worktree for each, and dispatches to idle Author workers.
* **Parameters:**
  * `mission_id` (string, required)

### `get_mission_status`
Returns real-time progress %, task states, squad roster, and blackboard facts count.

---

## 🔑 Two-Key Consensus Tools

### `submit_task_for_review`
Called by worker upon completing work in its isolated worktree. Transitions task into `REVIEW` status.
* **Parameters:**
  * `task_id` (string, required)
  * `worker_id` (string, required)
  * `summary` (string, required)

### `approve_review_key1`
Reviewer agent audits code diff against architectural and security standards, granting **Key 1**.
* **Parameters:**
  * `task_id` (string, required)
  * `reviewer_id` (string, optional, default: `"worker-reviewer"`)
  * `notes` (string, optional)

### `verify_tests_key2`
Verifier agent executes build and tests in sandbox, granting **Key 2**. When both keys are granted, transitions task to `MERGED`.
* **Parameters:**
  * `task_id` (string, required)
  * `verifier_id` (string, optional, default: `"worker-verifier"`)
  * `test_summary` (string, optional)

### `request_task_revisions`
Reviewer or Verifier rejects task draft with actionable critique, returning it to Author.

---

## 🌿 Worktree & Arbitration Tools

### `merge_task_worktree`
Merges a consensus-approved worker branch into the mission integration branch and automatically prunes the worktree directory.
* **Parameters:**
  * `mission_id` (string, required)
  * `task_id` (string, required)

---

## 📋 Blackboard & Event Bus Tools

### `broadcast_to_blackboard`
Broadcasts an interface definition, discovered schema, or API contract for peer workers.
* **Parameters:**
  * `mission_id` (string, required)
  * `topic` (string, required)
  * `content` (string, required)
  * `source_worker_id` (string, optional)

### `query_blackboard`
Queries shared facts discovered by peer workers.

---

## 🔍 Diagnostic Tools

### `check_fleet_health`
Returns orchestrator status, Git worktree availability, and database state.
