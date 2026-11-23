"""
NexusPilot Fleet - Git Worktree Multiplexer
Manages isolated disk worktrees per worker agent to enable zero-collision parallel coding.
"""

import subprocess
import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List


class GitWorktreeManager:
    def __init__(self, repo_root: Optional[str] = None):
        self.repo_root = Path(repo_root or os.getcwd()).resolve()

    def _run_git(self, args: List[str]) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["git", "-C", str(self.repo_root)] + args,
            capture_output=True,
            text=True,
            check=False
        )

    def is_git_repo(self) -> bool:
        res = self._run_git(["rev-parse", "--is-inside-work-tree"])
        return res.returncode == 0 and res.stdout.strip() == "true"

    def provision_worktree(
        self,
        worker_id: str,
        task_id: str,
        base_branch: str = "main"
    ) -> Dict[str, Any]:
        """
        Provisions a dedicated worktree directory and branch for a worker.
        Path: .fleet/worktrees/<worker_id>
        Branch: fleet/<worker_id>-<task_id>
        """
        fleet_worktrees_dir = self.repo_root / ".fleet" / "worktrees"
        fleet_worktrees_dir.mkdir(parents=True, exist_ok=True)

        clean_worker = worker_id.replace(" ", "_")
        clean_task = task_id.replace(" ", "_")
        worktree_path = fleet_worktrees_dir / clean_worker
        branch_name = f"fleet/{clean_worker}-{clean_task}"

        # Clean existing worktree directory if leftover
        if worktree_path.exists():
            self.prune_worktree(str(worktree_path), branch_name)

        if self.is_git_repo():
            # Check if branch exists
            check_branch = self._run_git(["rev-parse", "--verify", branch_name])
            if check_branch.returncode == 0:
                # Branch already exists, attach to it
                cmd = ["worktree", "add", str(worktree_path), branch_name]
            else:
                # Create branch from base_branch
                cmd = ["worktree", "add", "-b", branch_name, str(worktree_path), base_branch]

            res = self._run_git(cmd)
            if res.returncode != 0:
                # Fallback to local directory provision if git worktree command fails
                worktree_path.mkdir(parents=True, exist_ok=True)
        else:
            # Standalone directory simulation mode (non-git environments or tests)
            worktree_path.mkdir(parents=True, exist_ok=True)

        return {
            "worker_id": worker_id,
            "task_id": task_id,
            "worktree_path": str(worktree_path),
            "branch_name": branch_name,
            "status": "PROVISIONED"
        }

    def prune_worktree(self, worktree_path: str, branch_name: Optional[str] = None) -> bool:
        """Removes a worktree and prunes dangling references."""
        p = Path(worktree_path)
        if self.is_git_repo():
            self._run_git(["worktree", "remove", str(p), "--force"])
            self._run_git(["worktree", "prune"])

        if p.exists():
            shutil.rmtree(p, ignore_errors=True)

        return not p.exists()

    def list_worktrees(self) -> List[Dict[str, str]]:
        if not self.is_git_repo():
            fleet_dir = self.repo_root / ".fleet" / "worktrees"
            if not fleet_dir.exists():
                return []
            return [{"path": str(d), "branch": d.name} for d in fleet_dir.iterdir() if d.is_dir()]

        res = self._run_git(["worktree", "list", "--porcelain"])
        if res.returncode != 0:
            return []

        worktrees = []
        curr = {}
        for line in res.stdout.splitlines():
            line = line.strip()
            if line.startswith("worktree "):
                if curr:
                    worktrees.append(curr)
                curr = {"path": line.split(" ", 1)[1]}
            elif line.startswith("branch "):
                curr["branch"] = line.split(" ", 1)[1]
        if curr:
            worktrees.append(curr)
        return worktrees
