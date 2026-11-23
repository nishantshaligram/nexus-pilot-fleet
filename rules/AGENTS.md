# NexusPilot Fleet - Swarm Directives & Guardrails

These rules govern multi-agent task execution, isolated git worktree discipline, and Two-Key consensus approval.

## Rule 1: Zero Main Branch Contention
- Worker agents MUST NEVER commit code directly to `main` or `master`.
- All development and refactoring MUST occur exclusively inside the assigned isolated git worktree branch (`fleet/worker-<id>-<task>`).
- Code enters the integration pipeline only after passing Two-Key consensus and being merged by `merge_task_worktree`.

## Rule 2: Two-Key Triad Consensus
- Every author task requires two independent cryptographic sign-offs before merge:
  1. **Key 1 (Architecture & Security):** Granted via `approve_review_key1` by the Reviewer Agent after validating against project conventions and security standards.
  2. **Key 2 (Build & Tests):** Granted via `verify_tests_key2` by the Verifier Agent after compiling and executing the test suite in the sandbox.
- Single-agent sign-offs are strictly forbidden.

## Rule 3: Shared Blackboard Knowledge Broadcasting
- When a worker discovers or implements an API contract, shared interface, database schema, or reusable utility, it MUST immediately call `broadcast_to_blackboard`.
- Peer workers must query `query_blackboard` before re-implementing existing helpers.

## Rule 4: Clean Worktree Teardown
- Upon task verification and merge, worktrees must be pruned and cleaned up via `merge_task_worktree` to avoid dangling git lock references.
