"""
NexusPilot Fleet - Squad Manager
Provisions worker squad roles, manages state transitions, and matches model tiers.
"""

from typing import List, Dict, Any, Optional
import time
from bus.db import FleetDatabase


MODEL_TIERS = {
    "AUTHOR": "gemini-1.5-flash",
    "REVIEWER": "gemini-1.5-pro",
    "VERIFIER": "gemini-2.0-flash",
    "RESOLVER": "gemini-1.5-pro"
}


class SquadManager:
    def __init__(self, db: FleetDatabase):
        self.db = db

    def initialize_squad(self, mission_id: str, squad_size: int = 3) -> List[Dict[str, Any]]:
        """
        Creates a balanced squad for the mission:
        - 1 Lead Author (Coder)
        - Additional Authors if squad_size > 3
        - 1 Reviewer (Security & Architecture Auditor)
        - 1 Verifier (Test & Sandbox Runner)
        """
        workers = []

        # 1. Author Agents
        num_authors = max(1, squad_size - 2)
        for i in range(1, num_authors + 1):
            w_id = f"worker-author-{i}"
            w = self.db.register_worker(
                worker_id=w_id,
                mission_id=mission_id,
                role="AUTHOR",
                model=MODEL_TIERS["AUTHOR"]
            )
            workers.append(w)

        # 2. Reviewer Agent
        w_rev = self.db.register_worker(
            worker_id="worker-reviewer",
            mission_id=mission_id,
            role="REVIEWER",
            model=MODEL_TIERS["REVIEWER"]
        )
        workers.append(w_rev)

        # 3. Verifier Agent
        w_ver = self.db.register_worker(
            worker_id="worker-verifier",
            mission_id=mission_id,
            role="VERIFIER",
            model=MODEL_TIERS["VERIFIER"]
        )
        workers.append(w_ver)

        return workers

    def get_idle_worker(self, mission_id: str, role: str = "AUTHOR") -> Optional[Dict[str, Any]]:
        workers = self.db.get_workers_for_mission(mission_id)
        for w in workers:
            if w.get("role") == role and w.get("state") == "IDLE":
                return w
        return None

    def assign_worker_to_task(self, worker_id: str, task_id: str):
        self.db.update_worker_state(worker_id=worker_id, state="BUSY", current_task_id=task_id)

    def release_worker(self, worker_id: str):
        self.db.update_worker_state(worker_id=worker_id, state="IDLE", current_task_id=None)
