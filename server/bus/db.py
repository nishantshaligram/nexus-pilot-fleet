"""
NexusPilot Fleet - SQLite Mission Database & Event Store
Maintains durable state for missions, DAG tasks, workers, and shared blackboard.
"""

import sqlite3
import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

DEFAULT_FLEET_DIR_NAME = ".fleet"

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS missions (
    mission_id TEXT PRIMARY KEY,
    goal TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('PLANNING', 'ACTIVE', 'PAUSED', 'COMPLETED', 'FAILED')),
    base_branch TEXT NOT NULL,
    integration_branch TEXT NOT NULL,
    total_tokens INTEGER DEFAULT 0,
    total_cost_usd REAL DEFAULT 0.0,
    created_at INTEGER NOT NULL,
    completed_at INTEGER
);

CREATE TABLE IF NOT EXISTS tasks (
    task_id TEXT PRIMARY KEY,
    mission_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    dependencies TEXT, -- JSON array of prerequisite task_ids
    status TEXT NOT NULL CHECK(status IN ('PENDING', 'ASSIGNED', 'IN_PROGRESS', 'REVIEW', 'VERIFYING', 'MERGED', 'FAILED')),
    assigned_worker_id TEXT,
    worktree_path TEXT,
    branch_name TEXT,
    retry_count INTEGER DEFAULT 0,
    key1_approved INTEGER DEFAULT 0, -- Architecture & Security sign-off
    key2_approved INTEGER DEFAULT 0, -- Build & Test verification sign-off
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    FOREIGN KEY(mission_id) REFERENCES missions(mission_id)
);

CREATE TABLE IF NOT EXISTS workers (
    worker_id TEXT PRIMARY KEY,
    mission_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('AUTHOR', 'REVIEWER', 'VERIFIER', 'RESOLVER')),
    model TEXT NOT NULL,
    state TEXT NOT NULL CHECK(state IN ('IDLE', 'BUSY', 'STALLED', 'TERMINATED')),
    last_heartbeat INTEGER NOT NULL,
    current_task_id TEXT,
    FOREIGN KEY(mission_id) REFERENCES missions(mission_id)
);

CREATE TABLE IF NOT EXISTS blackboard (
    fact_id TEXT PRIMARY KEY,
    mission_id TEXT NOT NULL,
    topic TEXT NOT NULL,
    content TEXT NOT NULL,
    source_worker_id TEXT,
    created_at INTEGER NOT NULL,
    FOREIGN KEY(mission_id) REFERENCES missions(mission_id)
);

CREATE INDEX IF NOT EXISTS idx_tasks_mission ON tasks(mission_id, status);
CREATE INDEX IF NOT EXISTS idx_workers_heartbeat ON workers(last_heartbeat);
CREATE INDEX IF NOT EXISTS idx_blackboard_topic ON blackboard(mission_id, topic);
"""


class FleetDatabase:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is not None:
            p = Path(db_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            self.db_path = str(p)
        elif os.environ.get("FLEET_DB_PATH"):
            p = Path(os.environ["FLEET_DB_PATH"])
            p.parent.mkdir(parents=True, exist_ok=True)
            self.db_path = str(p)
        else:
            # Default to local plugin data directory
            data_dir = Path(__file__).resolve().parent.parent.parent / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = str(data_dir / "fleet_bus.db")

        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.executescript(SCHEMA_SQL)
            conn.commit()

    # --- Mission Operations ---
    def create_mission(self, mission_id: str, goal: str, base_branch: str = "main") -> Dict[str, Any]:
        now = int(time.time())
        integration_branch = f"fleet/integration-{mission_id}"
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO missions (mission_id, goal, status, base_branch, integration_branch, created_at)
                VALUES (?, ?, 'ACTIVE', ?, ?, ?)
                """,
                (mission_id, goal, base_branch, integration_branch, now)
            )
            conn.commit()
        return {
            "mission_id": mission_id,
            "goal": goal,
            "status": "ACTIVE",
            "base_branch": base_branch,
            "integration_branch": integration_branch,
            "created_at": now
        }

    def get_mission(self, mission_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM missions WHERE mission_id = ?", (mission_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def update_mission_status(self, mission_id: str, status: str):
        now = int(time.time()) if status in ("COMPLETED", "FAILED") else None
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE missions SET status = ?, completed_at = ? WHERE mission_id = ?",
                (status, now, mission_id)
            )
            conn.commit()

    # --- Task Operations ---
    def add_task(
        self,
        task_id: str,
        mission_id: str,
        title: str,
        description: str = "",
        dependencies: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        now = int(time.time())
        deps_json = json.dumps(dependencies or [])
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO tasks (task_id, mission_id, title, description, dependencies, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 'PENDING', ?, ?)
                """,
                (task_id, mission_id, title, description, deps_json, now, now)
            )
            conn.commit()
        return {
            "task_id": task_id,
            "mission_id": mission_id,
            "title": title,
            "dependencies": dependencies or [],
            "status": "PENDING"
        }

    def get_tasks_for_mission(self, mission_id: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM tasks WHERE mission_id = ? ORDER BY created_at ASC", (mission_id,))
            rows = cur.fetchall()
            result = []
            for r in rows:
                d = dict(r)
                d["dependencies"] = json.loads(d.get("dependencies") or "[]")
                result.append(d)
            return result

    def update_task_status(
        self,
        task_id: str,
        status: str,
        assigned_worker_id: Optional[str] = None,
        worktree_path: Optional[str] = None,
        branch_name: Optional[str] = None
    ):
        now = int(time.time())
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE tasks
                SET status = ?,
                    assigned_worker_id = COALESCE(?, assigned_worker_id),
                    worktree_path = COALESCE(?, worktree_path),
                    branch_name = COALESCE(?, branch_name),
                    updated_at = ?
                WHERE task_id = ?
                """,
                (status, assigned_worker_id, worktree_path, branch_name, now, task_id)
            )
            conn.commit()

    def update_consensus_keys(self, task_id: str, key1: Optional[bool] = None, key2: Optional[bool] = None):
        now = int(time.time())
        with self._get_connection() as conn:
            if key1 is not None:
                conn.execute("UPDATE tasks SET key1_approved = ?, updated_at = ? WHERE task_id = ?", (1 if key1 else 0, now, task_id))
            if key2 is not None:
                conn.execute("UPDATE tasks SET key2_approved = ?, updated_at = ? WHERE task_id = ?", (1 if key2 else 0, now, task_id))
            conn.commit()

    # --- Worker Operations ---
    def register_worker(self, worker_id: str, mission_id: str, role: str, model: str = "gemini-2.0-flash") -> Dict[str, Any]:
        now = int(time.time())
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO workers (worker_id, mission_id, role, model, state, last_heartbeat)
                VALUES (?, ?, ?, ?, 'IDLE', ?)
                """,
                (worker_id, mission_id, role, model, now)
            )
            conn.commit()
        return {"worker_id": worker_id, "mission_id": mission_id, "role": role, "model": model, "state": "IDLE"}

    def get_workers_for_mission(self, mission_id: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM workers WHERE mission_id = ?", (mission_id,))
            return [dict(r) for r in cur.fetchall()]

    def update_worker_state(self, worker_id: str, state: str, current_task_id: Optional[str] = None):
        now = int(time.time())
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE workers SET state = ?, current_task_id = ?, last_heartbeat = ? WHERE worker_id = ?",
                (state, current_task_id, now, worker_id)
            )
            conn.commit()

    # --- Blackboard Operations ---
    def post_fact(self, fact_id: str, mission_id: str, topic: str, content: str, source_worker_id: Optional[str] = None):
        now = int(time.time())
        with self._get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO blackboard (fact_id, mission_id, topic, content, source_worker_id, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (fact_id, mission_id, topic, content, source_worker_id, now)
            )
            conn.commit()

    def get_facts(self, mission_id: str, topic: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            if topic:
                cur.execute("SELECT * FROM blackboard WHERE mission_id = ? AND topic = ? ORDER BY created_at ASC", (mission_id, topic))
            else:
                cur.execute("SELECT * FROM blackboard WHERE mission_id = ? ORDER BY created_at ASC", (mission_id,))
            return [dict(r) for r in cur.fetchall()]
