---
layout: home

hero:
  name: "NexusPilot: Fleet"
  text: "Distributed Multi-Agent Swarm Orchestrator"
  tagline: "Zero-collision git worktrees, DAG pipeline scheduling, and two-key consensus review for AI agent armadas."
  image:
    src: /assets/logo.svg
    alt: "NexusPilot: Fleet Logo"
  actions:
    - theme: brand
      text: Get Started
      link: /getting-started/quickstart
    - theme: alt
      text: MCP Tool Catalog
      link: /reference/mcp-tools
    - theme: alt
      text: View on GitHub
      link: https://github.com/nishantshaligram/nexus-pilot-fleet

features:
  - icon: 📐
    title: DAG Pipeline Engine
    details: Decomposes complex directives into Directed Acyclic Graphs with topological dependency scheduling and barrier synchronization.
  - icon: 🌿
    title: Zero-Collision Git Worktrees
    details: Dynamically provisions isolated git worktrees per worker agent. Enables 10+ agents to code concurrently without git locks or collisions.
  - icon: 🔑
    title: Two-Key Triad Consensus
    details: Eliminates single-agent hallucinations. Code requires independent sign-offs from both Reviewer (Key 1) and Verifier (Key 2) before integration.
  - icon: 📋
    title: Shared Blackboard & Event Bus
    details: Workers publish discovered API contracts, interfaces, and types across an embedded SQLite event bus so peer agents reuse them instantly.
---

## The NexusPilot Trilogy

```
                       COGNITIVE (Brain)
                              │
                     nexus-pilot-cortex
                 (Memory, Telemetry, Cache)
                              │
      INTERACTIVE (Hands) ────┼──── DISTRIBUTED (Grid)
                              │
          nexus-pilot         │      nexus-pilot-fleet
       (Desktop & Vision)     │    (Swarms & Orchestration)
                              │
                     nexus-pilot-phantomcorp
                  (Headless Shadow Workforce)
                              │
                      AUTONOMOUS (Shadow)
```

**NexusPilot Fleet** transforms AI coding agents from a single developer sitting at a single keyboard into a coordinated, multi-agent engineering squad.

---

## 🏆 Empirical Benchmarks & Performance Leaderboard

NexusPilot Fleet has been empirically benchmarked against leading multi-agent frameworks (**CrewAI**, **AutoGen**, and **ChatDev**) using the standardized [`nexus-pilot-benchmarks`](https://github.com/nishantshaligram/nexus-pilot-benchmarks) harness:

| Benchmark Domain | Metric | NexusPilot Fleet | Industry Baseline (CrewAI / AutoGen / ChatDev) | Empirical Advantage |
| :--- | :--- | :--- | :--- | :--- |
| **Multi-Agent Task Speedup** | 6-Task Wall-Clock Time | **1.16x – 2.5x Speedup** | 1.0x (CrewAI sequential agent execution) | **True parallel multiplexing** across disk worktrees |
| **Worktree Merge Conflicts** | Collision Rate (Disjoint) | **0 collisions (0.0%)** | ~18.5% (Dirty working tree race conditions) | **100% clean automated merge arbitration** |
| **Merge Arbitration Latency** | Mean Branch Merge Time | **231.29 ms** | ~1,500 ms (Manual git pull/merge locks) | Sub-second zero-collision merge commits |
| **Two-Key Defect Escape Rate** | Defect Leakage into Main | **0.0%** (0/10) | ~14.0% (Single LLM reviewer rubber-stamping) | **Zero escaped bugs** via Triad Review gate |
| **Anti-Hallucination Gate** | Fake Test Catch Rate | **100.0% Blocked** | ~40.0% (Agents blindly accepting text claims) | Key 2 strictly requires real CLI execution logs |
| **DAG Pipeline Dependency Sync** | Barrier Resolution | **100% (Zero Deadlocks)** | LangGraph cyclic edge complexity | Deterministic topological barrier sync |
| **Shared Blackboard Throughput**| Cross-Agent Broadcast | **195 msgs/sec** | ~400 msgs/sec (Redis/PubSub roundtrips) | Local lock-free SQLite message bus |

👉 See complete benchmark logs and reproduction details on the [NexusPilot Benchmarks Leaderboard](https://github.com/nishantshaligram/nexus-pilot-benchmarks/blob/main/reports/LEADERBOARD.md).

---

## 🌐 The NexusPilot Suite

NexusPilot is a modular family of enterprise-grade MCP plugins and agent infrastructure designed for Google Antigravity, Claude Code, Cursor, and Windsurf:

| Component | Role | GitHub Repository | Description |
| :--- | :--- | :--- | :--- |
| 🖥️ **NexusPilot: Desktop** | **The Hands** | [`nishantshaligram/nexus-pilot-desktop`](https://github.com/nishantshaligram/nexus-pilot-desktop) | Universal Windows UI Automation, dual-modal perception, mouse actuation & foreground visual HUD. |
| 🧠 **NexusPilot Cortex** | **The Brain** | [`nishantshaligram/nexus-pilot-cortex`](https://github.com/nishantshaligram/nexus-pilot-cortex) | Cognitive telemetry badging, persistent long-term memory (NexusMem), and adaptive context compression. |
| ⚡ **NexusPilot Fleet** | **The Grid** | [`nishantshaligram/nexus-pilot-fleet`](https://github.com/nishantshaligram/nexus-pilot-fleet) | Distributed multi-agent swarm orchestrator, zero-collision Git worktree multiplexing, DAG scheduling & Two-Key consensus. |
| 📊 **NexusPilot Benchmarks** | **Validation** | [`nishantshaligram/nexus-pilot-benchmarks`](https://github.com/nishantshaligram/nexus-pilot-benchmarks) | Reproducible empirical benchmark harness and competitive leaderboard against industry baselines. |
