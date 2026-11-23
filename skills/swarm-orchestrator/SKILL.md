---
name: swarm-orchestrator
description: Distributed multi-agent mission planning, DAG topological scheduling, git worktree provisioning, and two-key consensus review for Antigravity.
---

# Swarm Orchestrator

This skill allows Antigravity agents to decompose large software engineering tasks into parallel execution pipelines and manage multi-agent worker squads.

## When to Use
- Decomposing large, multi-file refactoring or migration goals.
- Dispatching parallel worker agents on isolated git worktrees.
- Managing the Two-Key consensus approval pipeline (Author -> Reviewer -> Verifier).

## Key Tools
- `create_mission(goal, base_branch)`: Initializes mission and provisions squad roster.
- `decompose_goal(mission_id, goal)`: Breaks mission into topologically sorted DAG nodes.
- `dispatch_ready_tasks(mission_id)`: Dispatches ready tasks to idle Author workers.
- `submit_task_for_review(task_id, worker_id, summary)`: Submits draft PR for Triad review.
- `approve_review_key1(task_id, reviewer_id, notes)`: Reviewer sign-off on Architecture/Security.
- `verify_tests_key2(task_id, verifier_id, test_summary)`: Verifier sign-off on Builds/Tests.
- `merge_task_worktree(mission_id, task_id)`: Merges verified branch into integration branch and cleans worktree.
