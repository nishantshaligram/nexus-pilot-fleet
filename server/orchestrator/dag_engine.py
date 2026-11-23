"""
NexusPilot Fleet - DAG Pipeline Engine
Decomposes high-level missions into Directed Acyclic Graphs with topological dependency scheduling.
"""

from typing import List, Dict, Any, Set, Optional
from collections import defaultdict, deque
import re
import hashlib
import time


class CycleDetectedError(Exception):
    pass


class DAGEngine:
    def __init__(self, tasks: Optional[List[Dict[str, Any]]] = None):
        self.tasks: Dict[str, Dict[str, Any]] = {}
        if tasks:
            for t in tasks:
                self.tasks[t["task_id"]] = t

    def add_task(
        self,
        task_id: str,
        title: str,
        description: str = "",
        dependencies: Optional[List[str]] = None,
        status: str = "PENDING"
    ):
        self.tasks[task_id] = {
            "task_id": task_id,
            "title": title,
            "description": description,
            "dependencies": dependencies or [],
            "status": status,
            "key1_approved": 0,
            "key2_approved": 0
        }
        self.validate_dag()

    def validate_dag(self):
        """Validates that the task graph contains no circular dependencies."""
        graph = defaultdict(list)
        all_nodes = set(self.tasks.keys())
        for tid, t in self.tasks.items():
            for dep in t.get("dependencies", []):
                if dep in all_nodes:
                    graph[dep].append(tid)

        visited = {}  # 0 = unvisited, 1 = visiting (grey), 2 = visited (black)
        for node in all_nodes:
            visited[node] = 0

        def dfs(u: str):
            visited[u] = 1
            for v in graph[u]:
                if visited[v] == 1:
                    raise CycleDetectedError(f"Circular dependency detected involving task '{v}' and '{u}'")
                if visited[v] == 0:
                    dfs(v)
            visited[u] = 2

        for node in all_nodes:
            if visited[node] == 0:
                dfs(node)

    def topological_sort(self) -> List[str]:
        """Returns task IDs in topological dependency execution order."""
        self.validate_dag()
        in_degree = {tid: 0 for tid in self.tasks}
        graph = defaultdict(list)

        for tid, t in self.tasks.items():
            for dep in t.get("dependencies", []):
                if dep in self.tasks:
                    graph[dep].append(tid)
                    in_degree[tid] += 1

        queue = deque([tid for tid, deg in in_degree.items() if deg == 0])
        ordered = []

        while queue:
            curr = queue.popleft()
            ordered.append(curr)
            for neighbor in graph[curr]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        return ordered

    def get_ready_tasks(self) -> List[Dict[str, Any]]:
        """
        Returns all tasks that are currently PENDING and whose prerequisite
        dependencies are fully satisfied (status == 'MERGED' or 'COMPLETED').
        """
        ready = []
        for tid, t in self.tasks.items():
            if t.get("status") != "PENDING":
                continue
            deps = t.get("dependencies", [])
            deps_satisfied = all(
                dep in self.tasks and self.tasks[dep].get("status") in ("MERGED", "COMPLETED")
                for dep in deps
            )
            if deps_satisfied:
                ready.append(t)
        return ready

    def get_progress_pct(self) -> float:
        if not self.tasks:
            return 0.0
        completed = sum(1 for t in self.tasks.values() if t.get("status") in ("MERGED", "COMPLETED"))
        return round((completed / len(self.tasks)) * 100.0, 1)


def decompose_goal_to_dag(goal: str, mission_id: str) -> List[Dict[str, Any]]:
    """
    Decomposes a high-level software engineering goal into a staged DAG.
    Generates topological tasks: Specification -> Parallel Implementation -> Test Verification -> Documentation.
    """
    clean_goal = goal.strip()
    mid_hash = hashlib.sha256(f"{clean_goal}_{time.time()}".encode()).hexdigest()[:6]

    # Detect multi-file or multi-component cues in prompt
    has_tests = bool(re.search(r"test|suite|coverage|verify", clean_goal, re.IGNORECASE))
    has_docs = bool(re.search(r"doc|readme|openapi|swagger", clean_goal, re.IGNORECASE))
    has_api = bool(re.search(r"api|endpoint|controller|route|graphql", clean_goal, re.IGNORECASE))

    tasks = []

    # Node 1: Specification & Architecture Contract
    t1_id = f"T1_{mid_hash}"
    tasks.append({
        "task_id": t1_id,
        "title": "Architecture Contract & Dependency Discovery",
        "description": f"Analyze codebase interfaces and define shared types/contracts for: {clean_goal}",
        "dependencies": []
    })

    # Nodes 2 & 3: Implementation tasks (Parallel execution)
    t2_id = f"T2_{mid_hash}"
    tasks.append({
        "task_id": t2_id,
        "title": "Core Implementation & Feature Logic (Slice A)",
        "description": f"Implement core modules and business logic for: {clean_goal}",
        "dependencies": [t1_id]
    })

    t3_id = f"T3_{mid_hash}"
    if has_api:
        title_t3 = "API Routes & Schema Validation (Slice B)"
    else:
        title_t3 = "Supporting Utilities & State Integration (Slice B)"

    tasks.append({
        "task_id": t3_id,
        "title": title_t3,
        "description": f"Implement supporting handlers, converters, or integration points for: {clean_goal}",
        "dependencies": [t1_id]
    })

    # Node 4: Integration Test Suite
    t4_id = f"T4_{mid_hash}"
    tasks.append({
        "task_id": t4_id,
        "title": "Integration Test Suite & Regression Verification",
        "description": f"Develop automated unit/integration tests verifying functionality of: {clean_goal}",
        "dependencies": [t2_id, t3_id]
    })

    # Node 5: Documentation & Final Integration Review
    t5_id = f"T5_{mid_hash}"
    tasks.append({
        "task_id": t5_id,
        "title": "Documentation, Type Export & Consensus Sign-Off",
        "description": f"Update API documentation, README references, and obtain final peer sign-off for: {clean_goal}",
        "dependencies": [t4_id]
    })

    return tasks
