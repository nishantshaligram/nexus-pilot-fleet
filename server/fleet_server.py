"""
NexusPilot Fleet - Model Context Protocol (MCP) Server
Distributed Multi-Agent Swarm Orchestrator:
1. DAG Task Pipeline Scheduler & Dependency Engine
2. Zero-Collision Git Worktree Multiplexer
3. Two-Key Consensus Protocol (Author -> Reviewer -> Verifier)
4. Shared Blackboard & Inter-Agent Event Bus
"""

import sys
import os
import uuid
from typing import Optional, List, Dict, Any

# Ensure current server directory is on path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURRENT_DIR)

from bus import FleetDatabase, Blackboard
from orchestrator import DAGEngine, SquadManager, decompose_goal_to_dag
from worktree import GitWorktreeManager, MergeArbitrator
from consensus import ReviewProtocol

try:
    from mcp.server.mcpserver import MCPServer
except ImportError:
    try:
        from mcp.server.fastmcp import FastMCP as MCPServer
    except ImportError:
        raise RuntimeError("mcp Python SDK is required. Run 'pip install mcp'")

# Instantiate core engines
db = FleetDatabase()
blackboard = Blackboard(db)
squad_manager = SquadManager(db)
worktree_manager = GitWorktreeManager()
merge_arbitrator = MergeArbitrator()
review_protocol = ReviewProtocol(db)

server = MCPServer("nexus-pilot-fleet")


# ==============================================================================
# Pillar 1: Mission & DAG Orchestration Tools
# ==============================================================================

@server.tool()
def create_mission(
    goal: str,
    base_branch: str = "main",
    mission_id: Optional[str] = None
) -> dict:
    """
    Initializes a new multi-agent mission with a high-level software engineering goal.
    Provisions initial mission record and spawns a dedicated worker squad.
    """
    m_id = mission_id or f"msn_{uuid.uuid4().hex[:8]}"
    mission = db.create_mission(mission_id=m_id, goal=goal, base_branch=base_branch)
    squad = squad_manager.initialize_squad(mission_id=m_id)
    
    return {
        "status": "MISSION_INITIALIZED",
        "mission": mission,
        "squad_roster": squad,
        "instructions": "Call 'decompose_goal' to plan and schedule the DAG execution pipeline."
    }


@server.tool()
def decompose_goal(
    mission_id: str,
    goal: Optional[str] = None
) -> dict:
    """
    Decomposes a mission goal into a staged Directed Acyclic Graph (DAG) with
    dependencies and registers tasks in the database.
    """
    mission = db.get_mission(mission_id)
    if not mission:
        return {"error": f"Mission '{mission_id}' not found."}

    target_goal = goal or mission["goal"]
    generated_tasks = decompose_goal_to_dag(target_goal, mission_id)

    registered = []
    for t in generated_tasks:
        reg = db.add_task(
            task_id=t["task_id"],
            mission_id=mission_id,
            title=t["title"],
            description=t["description"],
            dependencies=t["dependencies"]
        )
        registered.append(reg)

    return {
        "mission_id": mission_id,
        "tasks_count": len(registered),
        "dag_nodes": registered
    }


@server.tool()
def dispatch_ready_tasks(mission_id: str) -> dict:
    """
    Scans the DAG for PENDING tasks whose dependencies are satisfied, provisions
    an isolated git worktree for each, and assigns them to idle Author workers.
    """
    all_tasks = db.get_tasks_for_mission(mission_id)
    dag = DAGEngine(all_tasks)
    ready = dag.get_ready_tasks()

    dispatched = []
    for task in ready:
        worker = squad_manager.get_idle_worker(mission_id, role="AUTHOR")
        if not worker:
            break

        # Provision isolated git worktree
        wt = worktree_manager.provision_worktree(
            worker_id=worker["worker_id"],
            task_id=task["task_id"],
            base_branch="main"
        )

        # Update DB state
        db.update_task_status(
            task_id=task["task_id"],
            status="IN_PROGRESS",
            assigned_worker_id=worker["worker_id"],
            worktree_path=wt["worktree_path"],
            branch_name=wt["branch_name"]
        )
        squad_manager.assign_worker_to_task(worker["worker_id"], task["task_id"])

        dispatched.append({
            "task_id": task["task_id"],
            "title": task["title"],
            "worker_id": worker["worker_id"],
            "worktree_path": wt["worktree_path"],
            "branch_name": wt["branch_name"]
        })

    return {
        "mission_id": mission_id,
        "dispatched_count": len(dispatched),
        "dispatched_tasks": dispatched,
        "pending_dependencies_count": len(ready) - len(dispatched)
    }


@server.tool()
def get_mission_status(mission_id: str) -> dict:
    """
    Returns real-time mission status, DAG completion %, squad roster, and blackboard facts.
    """
    mission = db.get_mission(mission_id)
    if not mission:
        return {"error": f"Mission '{mission_id}' not found."}

    tasks = db.get_tasks_for_mission(mission_id)
    workers = db.get_workers_for_mission(mission_id)
    facts = blackboard.query(mission_id)

    dag = DAGEngine(tasks)
    progress_pct = dag.get_progress_pct()

    return {
        "mission_id": mission_id,
        "goal": mission["goal"],
        "status": mission["status"],
        "progress_pct": progress_pct,
        "tasks": tasks,
        "workers": workers,
        "blackboard_facts_count": len(facts)
    }


# ==============================================================================
# Pillar 2: Two-Key Consensus Protocol Tools
# ==============================================================================

@server.tool()
def submit_task_for_review(
    task_id: str,
    worker_id: str,
    summary: str
) -> dict:
    """
    Worker calls this upon completing work in its isolated worktree.
    Transitions task into 'REVIEW' status for Triad evaluation.
    """
    return review_protocol.submit_draft(task_id, worker_id, summary)


@server.tool()
def approve_review_key1(
    task_id: str,
    reviewer_id: str = "worker-reviewer",
    notes: str = "Architecture, security, and edge-cases validated."
) -> dict:
    """
    Reviewer agent audits code diff against architectural and security standards.
    Grants Key 1 sign-off and advances task to test verification.
    """
    return review_protocol.sign_off_key1_architecture(task_id, reviewer_id, notes)


@server.tool()
def verify_tests_key2(
    task_id: str,
    verifier_id: str = "worker-verifier",
    test_summary: str = "Test suite passed with zero regressions."
) -> dict:
    """
    Verifier agent executes build and tests in the sandbox.
    Grants Key 2 sign-off. When both keys are granted, task transitions to 'MERGED'.
    """
    return review_protocol.sign_off_key2_tests(task_id, verifier_id, test_summary)


@server.tool()
def request_task_revisions(
    task_id: str,
    reviewer_id: str,
    critique: str
) -> dict:
    """
    Reviewer or Verifier rejects task draft with actionable critique, returning it to Author.
    """
    return review_protocol.request_revisions(task_id, reviewer_id, critique)


# ==============================================================================
# Pillar 3: Worktree Management & Merge Arbitration
# ==============================================================================

@server.tool()
def merge_task_worktree(
    mission_id: str,
    task_id: str
) -> dict:
    """
    Merges a consensus-approved worker branch into the mission integration branch
    and automatically cleans up the worker worktree.
    """
    tasks = db.get_tasks_for_mission(mission_id)
    target_task = next((t for t in tasks if t["task_id"] == task_id), None)
    if not target_task:
        return {"error": f"Task '{task_id}' not found."}

    if not (target_task.get("key1_approved") and target_task.get("key2_approved")):
        return {"error": "Two-Key consensus not achieved. Both Key 1 and Key 2 sign-offs required."}

    mission = db.get_mission(mission_id)
    branch = target_task.get("branch_name")
    wt_path = target_task.get("worktree_path")
    integration_branch = mission["integration_branch"]

    # Perform merge arbitration
    merge_res = merge_arbitrator.merge_worker_branch(
        worker_branch=branch,
        integration_branch=integration_branch
    )

    # Release worker and prune worktree
    if wt_path:
        worktree_manager.prune_worktree(wt_path, branch)

    assigned_worker = target_task.get("assigned_worker_id")
    if assigned_worker:
        squad_manager.release_worker(assigned_worker)

    return {
        "status": "MERGED_AND_PRUNED",
        "task_id": task_id,
        "merge_result": merge_res
    }


# ==============================================================================
# Pillar 4: Shared Blackboard Tools
# ==============================================================================

@server.tool()
def broadcast_to_blackboard(
    mission_id: str,
    topic: str,
    content: str,
    source_worker_id: Optional[str] = None
) -> dict:
    """
    Broadcasts a discovered architectural contract, new interface, or shared pattern
    to all other workers in the swarm.
    """
    fact_id = blackboard.broadcast(
        mission_id=mission_id,
        topic=topic,
        content=content,
        source_worker_id=source_worker_id
    )
    return {
        "status": "BROADCASTED",
        "fact_id": fact_id,
        "topic": topic
    }


@server.tool()
def query_blackboard(
    mission_id: str,
    topic: Optional[str] = None
) -> list:
    """
    Queries shared facts discovered by peer workers during the mission.
    """
    return blackboard.query(mission_id=mission_id, topic=topic)


# ==============================================================================
# Pillar 5: Health & Diagnostic Tools
# ==============================================================================

@server.tool()
def check_fleet_health() -> dict:
    """
    Verifies Fleet swarm orchestrator, Git worktree availability, and database state.
    """
    is_git = worktree_manager.is_git_repo()
    worktrees = worktree_manager.list_worktrees()
    return {
        "status": "online",
        "engine": "NexusPilot Fleet",
        "version": "1.0.0",
        "is_git_repo": is_git,
        "database_path": db.db_path,
        "active_worktrees_count": len(worktrees)
    }


def main():
    """Runs the MCP server over stdio."""
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
