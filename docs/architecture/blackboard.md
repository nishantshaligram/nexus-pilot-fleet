# Architecture: Shared Blackboard & Event Bus

The Shared Blackboard allows asynchronous worker squads to share discoveries, API contracts, and interface definitions in real time.

---

## 1. Problem: Redundant Reinvention
In naive multi-agent systems, each worker acts in isolation:
* Worker A invents a helper `formatCurrency(val)`.
* Worker B, running on another branch, creates a conflicting `formatMoney(val)`.
* Merge conflicts and duplicate implementations proliferate.

---

## 2. Solution: The Blackboard Broadcast Pattern

```mermaid
flowchart LR
    WorkerA["Worker A (Auth)"] -->|broadcast_to_blackboard('jwt_format', ...)| Blackboard[("SQLite Shared Blackboard<br/>(.fleet/fleet_bus.db)")]
    Blackboard -->|query_blackboard('jwt_format')| WorkerB["Worker B (Billing)"]
    Blackboard -->|query_blackboard()| WorkerC["Worker C (E2E Tests)"]
```

When any worker implements or discovers a contract:
1. Calls `broadcast_to_blackboard(mission_id, topic, content)`.
2. The fact is persisted with timestamp and source worker attribution.
3. Peer workers query `query_blackboard` before designing new types or interfaces.
