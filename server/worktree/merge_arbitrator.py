"""
NexusPilot Fleet - Merge Arbitrator
Stages and merges verified worker branches into the mission integration branch.
"""

import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List


class MergeArbitrator:
    def __init__(self, repo_root: Optional[str] = None):
        self.repo_root = Path(repo_root or ".").resolve()

    def _run_git(self, args: List[str]) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["git", "-C", str(self.repo_root)] + args,
            capture_output=True,
            text=True,
            check=False
        )

    def merge_worker_branch(
        self,
        worker_branch: str,
        integration_branch: str
    ) -> Dict[str, Any]:
        """
        Attempts to merge a completed worker branch into the mission integration branch.
        """
        # 1. Switch to or create integration branch
        check_int = self._run_git(["rev-parse", "--verify", integration_branch])
        if check_int.returncode != 0:
            self._run_git(["branch", integration_branch])

        # 2. Perform merge in clean worktree or branch
        merge_res = self._run_git(["merge", worker_branch, "-m", f"fleet: merge {worker_branch} into {integration_branch}"])
        
        if merge_res.returncode == 0:
            return {
                "success": True,
                "status": "MERGED",
                "worker_branch": worker_branch,
                "integration_branch": integration_branch,
                "message": "Clean merge succeeded."
            }

        # Conflict detected
        if "CONFLICT" in merge_res.stdout or "CONFLICT" in merge_res.stderr:
            # Abort raw merge to avoid dirtying tree
            self._run_git(["merge", "--abort"])
            return {
                "success": False,
                "status": "CONFLICT",
                "worker_branch": worker_branch,
                "integration_branch": integration_branch,
                "message": "Non-trivial merge conflict detected; dispatched to Resolver Agent."
            }

        return {
            "success": False,
            "status": "FAILED",
            "worker_branch": worker_branch,
            "integration_branch": integration_branch,
            "error": merge_res.stderr or merge_res.stdout
        }
