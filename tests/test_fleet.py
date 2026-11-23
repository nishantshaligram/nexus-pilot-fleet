"""
NexusPilot Fleet - Automated Test Suite
Validates DAG scheduling, Worktree provisioning, Two-Key Consensus, and Blackboard.
"""

import os
import sys
import tempfile
import unittest

# Ensure server module is accessible
SERVER_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "server"))
if SERVER_DIR not in sys.path:
    sys.path.insert(0, SERVER_DIR)

from bus import FleetDatabase, Blackboard
from orchestrator import DAGEngine, SquadManager, decompose_goal_to_dag, CycleDetectedError
from worktree import GitWorktreeManager, MergeArbitrator
from consensus import ReviewProtocol


class TestFleet(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_fleet.db")
        self.db = FleetDatabase(self.db_path)
        self.blackboard = Blackboard(self.db)
        self.squad_manager = SquadManager(self.db)
        self.worktree_manager = GitWorktreeManager(repo_root=self.temp_dir.name)
        self.review_protocol = ReviewProtocol(self.db)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_dag_dependency_and_ready_tasks(self):
        dag = DAGEngine()
        dag.add_task("T1", "Schema Definition", dependencies=[])
        dag.add_task("T2", "User Module", dependencies=["T1"])
        dag.add_task("T3", "Billing Module", dependencies=["T1"])
        dag.add_task("T4", "E2E Tests", dependencies=["T2", "T3"])

        # Topo sort validation
        order = dag.topological_sort()
        self.assertEqual(order[0], "T1")
        self.assertEqual(order[-1], "T4")

        # Ready tasks (only T1 initially)
        ready = dag.get_ready_tasks()
        self.assertEqual(len(ready), 1)
        self.assertEqual(ready[0]["task_id"], "T1")

        # Mark T1 merged
        dag.tasks["T1"]["status"] = "MERGED"
        ready_after_t1 = dag.get_ready_tasks()
        self.assertEqual(len(ready_after_t1), 2)
        ready_ids = {t["task_id"] for t in ready_after_t1}
        self.assertEqual(ready_ids, {"T2", "T3"})

    def test_dag_cycle_detection(self):
        dag = DAGEngine()
        dag.add_task("A", "Task A", dependencies=["B"])
        with self.assertRaises(CycleDetectedError):
            dag.add_task("B", "Task B", dependencies=["A"])

    def test_goal_decomposition(self):
        tasks = decompose_goal_to_dag("Refactor user auth API endpoints and add tests", "m1")
        self.assertGreaterEqual(len(tasks), 4)
        task_ids = [t["task_id"] for t in tasks]
        # First task should have zero dependencies
        self.assertEqual(len(tasks[0]["dependencies"]), 0)
        # Downstream tasks must depend on earlier ones
        self.assertTrue(any(task_ids[0] in t["dependencies"] for t in tasks[1:]))

    def test_squad_registration(self):
        squad = self.squad_manager.initialize_squad("test_mission", squad_size=3)
        self.assertEqual(len(squad), 3)
        roles = {w["role"] for w in squad}
        self.assertIn("AUTHOR", roles)
        self.assertIn("REVIEWER", roles)
        self.assertIn("VERIFIER", roles)

    def test_two_key_consensus_lifecycle(self):
        self.db.create_mission("m_test", "Refactor controllers")
        self.db.add_task("task_01", "m_test", "Implement JWT auth")

        # 1. Author submits draft
        sub = self.review_protocol.submit_draft("task_01", "worker-author-1", "Implemented JWT logic")
        self.assertEqual(sub["status"], "REVIEW")

        # 2. Reviewer signs off on Key 1
        k1 = self.review_protocol.sign_off_key1_architecture("task_01", "worker-reviewer")
        self.assertTrue(k1["key1_approved"])

        # 3. Verifier signs off on Key 2
        k2 = self.review_protocol.sign_off_key2_tests("task_01", "worker-verifier")
        self.assertTrue(k2["key2_approved"])
        self.assertEqual(k2["status"], "MERGED")

    def test_shared_blackboard(self):
        f_id = self.blackboard.broadcast(
            mission_id="m_facts",
            topic="api_contract",
            content="Auth header format: Bearer <jwt_token>",
            source_worker_id="worker-author-1"
        )
        self.assertTrue(f_id.startswith("fact_"))

        facts = self.blackboard.query("m_facts", topic="api_contract")
        self.assertEqual(len(facts), 1)
        self.assertIn("Bearer", facts[0]["content"])

    def test_worktree_provision_and_pruning(self):
        wt = self.worktree_manager.provision_worktree("worker_1", "task_01", "main")
        self.assertTrue(os.path.exists(wt["worktree_path"]))
        self.assertIn("fleet/worker_1-task_01", wt["branch_name"])

        # Prune
        pruned = self.worktree_manager.prune_worktree(wt["worktree_path"], wt["branch_name"])
        self.assertTrue(pruned)
        self.assertFalse(os.path.exists(wt["worktree_path"]))


if __name__ == "__main__":
    unittest.main()
