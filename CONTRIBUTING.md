# Contributing to NexusPilot Fleet

Thank you for your interest in contributing to **NexusPilot Fleet**!  
Fleet is the distributed multi-agent swarm orchestrator of the NexusPilot family, providing zero-collision git worktree multiplexing, DAG pipeline scheduling, and Two-Key consensus review.

---

## 🛠️ Development Setup

### 1. Prerequisites
- Git 2.5+ (Required for `git worktree` isolation)
- Python 3.10+ (Standard library, 0 required external dependencies)
- Node.js 18+ (For NPX CLI and VitePress documentation)

### 2. Clone and Setup
```bash
git clone https://github.com/nishantshaligram/nexus-pilot-fleet.git
cd nexus-pilot-fleet
```

### 3. Run Environment Diagnostics
```bash
node ./bin/nexus-pilot-fleet.js doctor
```

### 4. Run Automated Test Suite
```bash
python tests/run_tests.py
```

---

## 🚀 Contribution Workflow

1. **Fork & Branch:** Create a feature branch from `main`:
   ```bash
   git checkout -b feat/your-feature-name
   ```
2. **Follow Conventions:**
   - Python: Standard library priority, clean type annotations.
   - Node.js: ES Module (`type: module`).
   - Git Safety: Ensure all worktree actions isolate disk copies and prune cleanly.
3. **Tests:** Ensure all unit tests pass with `python tests/run_tests.py` and add test cases for new capabilities.
4. **Pull Requests:** Open a PR against `main` with a clear explanation of changes and test results.
