"""
NexusPilot Fleet - Two-Key Consensus Protocol
Implements the Triad Review Lifecycle: Author -> Reviewer (Key 1) -> Verifier (Key 2).
"""

from typing import Dict, Any, Optional
from bus.db import FleetDatabase


class ReviewProtocol:
    def __init__(self, db: FleetDatabase):
        self.db = db

    def submit_draft(
        self,
        task_id: str,
        worker_id: str,
        summary: str
    ) -> Dict[str, Any]:
        """Worker (Author) submits completed task for Triad Review."""
        self.db.update_task_status(task_id=task_id, status="REVIEW", assigned_worker_id=worker_id)
        return {
            "task_id": task_id,
            "status": "REVIEW",
            "summary": summary,
            "next_step": "Awaiting Reviewer Agent audit (Key 1)"
        }

    def sign_off_key1_architecture(
        self,
        task_id: str,
        reviewer_id: str,
        notes: str = "Architecture and security guidelines approved."
    ) -> Dict[str, Any]:
        """Reviewer Agent inspects diff and grants Key 1 (Architecture & Security)."""
        self.db.update_consensus_keys(task_id=task_id, key1=True)
        self.db.update_task_status(task_id=task_id, status="VERIFYING")
        return {
            "task_id": task_id,
            "key1_approved": True,
            "reviewer_id": reviewer_id,
            "notes": notes,
            "next_step": "Awaiting Verifier Agent sandbox build and test execution (Key 2)"
        }

    def sign_off_key2_tests(
        self,
        task_id: str,
        verifier_id: str,
        test_summary: str = "All tests and builds passed with exit code 0."
    ) -> Dict[str, Any]:
        """Verifier Agent executes build/tests and grants Key 2 (Build & Tests)."""
        self.db.update_consensus_keys(task_id=task_id, key2=True)
        self.db.update_task_status(task_id=task_id, status="MERGED")
        return {
            "task_id": task_id,
            "key1_approved": True,
            "key2_approved": True,
            "status": "MERGED",
            "verifier_id": verifier_id,
            "test_summary": test_summary,
            "next_step": "Task fully verified by consensus. Ready for integration branch merge."
        }

    def request_revisions(
        self,
        task_id: str,
        reviewer_id: str,
        critique: str
    ) -> Dict[str, Any]:
        """Reviewer or Verifier rejects draft and returns feedback to Author."""
        self.db.update_consensus_keys(task_id=task_id, key1=False, key2=False)
        self.db.update_task_status(task_id=task_id, status="IN_PROGRESS")
        return {
            "task_id": task_id,
            "status": "IN_PROGRESS",
            "reviewer_id": reviewer_id,
            "critique": critique,
            "action": "Returned to Author agent for refactoring."
        }
