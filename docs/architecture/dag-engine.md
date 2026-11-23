# Architecture: DAG Pipeline Engine

The Directed Acyclic Graph (DAG) Pipeline Engine manages goal decomposition, dependency graphs, cycle prevention, and topological scheduling.

---

## 1. Topological Scheduling Pipeline

```mermaid
flowchart TD
    Goal["High-Level User Goal\n('Refactor 30 REST Endpoints to Fastify')"] --> Decomposer["Autonomous Decomposer\n(decompose_goal_to_dag)"]

    Decomposer --> T1["T1: Interface & Schema Specs\n(Dependencies: None)"]
    T1 --> T2["T2: Auth Handlers\n(Deps: T1)"]
    T1 --> T3["T3: Billing Handlers\n(Deps: T1)"]
    
    subgraph ParallelExecution["Parallel Worker Execution"]
        T2
        T3
    end

    T2 & T3 --> T4["T4: Integration Test Suite\n(Barrier Synchronization: Requires T2 & T3)"]
    T4 --> T5["T5: Docs & Sign-Off\n(Deps: T4)"]
```

---

## 2. Dependency Resolution & Barrier Synchronization

A task transitions to `READY` status if and only if:
1. Its current status is `PENDING`.
2. Every task ID in its `dependencies` array has achieved status `MERGED` or `COMPLETED`.

This guarantees that downstream workers never build against unverified or half-implemented upstream code.

---

## 3. Cycle Detection
Fleet runs a depth-first search (DFS) with 3-color node tracking (white, grey, black) upon every graph modification. If a circular dependency is detected, Fleet immediately rejects the task with `CycleDetectedError` to prevent agent deadlocks.
