---
name: mission-control
description: Inspects active multi-agent mission status, DAG completion progress, squad health, and inter-agent blackboard facts.
---

# Mission Control

This skill allows agents and users to monitor real-time multi-agent mission execution.

## When to Use
- Inspecting active tasks, worker branches, and progress percentage.
- Querying the shared blackboard for contracts and interfaces discovered by peer agents.
- Diagnosing stalled or blocked tasks.

## Key Tools
- `get_mission_status(mission_id)`: Real-time progress, task states, and squad roster.
- `broadcast_to_blackboard(mission_id, topic, content)`: Publishes shared knowledge.
- `query_blackboard(mission_id, topic)`: Queries facts shared by peer workers.
- `check_fleet_health()`: Diagnostic check on git worktree and database subsystem.
