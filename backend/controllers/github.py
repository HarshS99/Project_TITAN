"""
Project TITAN — GitHub Controller
Full GitHub automation: create repos, manage branches, commit, push,
generate releases, create issues, and more.
Uses PyGithub (REST API) + GitPython (local git) + gh CLI.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

import git
from github import Github, GithubException
from loguru import logger

from backend.config import GITHUB_TOKEN, GITHUB_USERNAME


@dataclass
class RepoInfo:
    name: str
    full_name: str
    url: str
    clone_url: str
    ssh_url: str
    branches: list[str] = field(default_factory=list)
    default_branch: str = "main"


class GitHubController:
    """
    Full GitHub automation controller.
    - Local git ops via GitPython
    - Remote GitHub ops via PyGithub REST API
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self._gh = Github(GITHUB_TOKEN) if GITHUB_TOKEN else None
        self._user = None
        self._username = GITHUB_USERNAME

        if self._gh:
            try:
                self._user = self._gh.get_user()
                if not self._username:
                    self._username = self._user.login
                logger.info(f"GitHub connected as: {self._username}")
            except GithubException as e:
                logger.error(f"GitHub auth failed: {e}")

    # ── Local Git Operations ───────────────────────────────────

    def git_init(self) -> bool:
        """Initialize a git repo in the project directory."""
        try:
            if (self.project_root / ".git").exists():
                logger.info("Git already initialized")
                self._repo = git.Repo(self.project_root)
                return True
            self._repo = git.Repo.init(self.project_root)
            logger.success("✅ Git initialized")
            return True
        except Exception as e:
            logger.error(f"git init failed: {e}")
            return False

    def _get_repo(self) -> git.Repo:
        if not hasattr(self, "_repo"):
            self._repo = git.Repo(self.project_root)
        return self._repo

    def git_add_all(self) -> bool:
        """Stage all changes."""
        try:
            repo = self._get_repo()
            repo.git.add(A=True)
            logger.info("📦 Staged all changes")
            return True
        except Exception as e:
            logger.error(f"git add failed: {e}")
            return False

    def git_commit(self, message: str) -> bool:
        """Create a commit."""
        try:
            repo = self._get_repo()
            if not repo.index.diff("HEAD") and not repo.untracked_files:
                # Check if there's anything to commit
                try:
                    repo.head.commit  # Will fail if no commits yet
                    logger.info("Nothing to commit")
                    return True
                except Exception:
                    pass  # First commit, continue

            repo.index.commit(message)
            logger.success(f"✅ Committed: {message}")
            return True
        except Exception as e:
            logger.error(f"git commit failed: {e}")
            return False

    def create_branch(self, branch_name: str, checkout: bool = True) -> bool:
        """Create and optionally checkout a branch."""
        try:
            repo = self._get_repo()
            new_branch = repo.create_head(branch_name)
            if checkout:
                new_branch.checkout()
            logger.success(f"✅ Created branch: {branch_name}")
            return True
        except Exception as e:
            logger.error(f"create_branch failed: {e}")
            return False

    def checkout_branch(self, branch_name: str) -> bool:
        """Switch to an existing branch."""
        try:
            repo = self._get_repo()
            repo.git.checkout(branch_name)
            return True
        except Exception as e:
            logger.error(f"checkout failed: {e}")
            return False

    def set_remote(self, remote_url: str, remote_name: str = "origin") -> bool:
        """Set the remote URL."""
        try:
            repo = self._get_repo()
            if remote_name in [r.name for r in repo.remotes]:
                repo.remote(remote_name).set_url(remote_url)
            else:
                repo.create_remote(remote_name, remote_url)
            logger.info(f"Remote set: {remote_url}")
            return True
        except Exception as e:
            logger.error(f"set_remote failed: {e}")
            return False

    def git_push(self, branch: str = "main", remote: str = "origin", force: bool = False) -> bool:
        """Push to remote."""
        try:
            repo = self._get_repo()
            remote_obj = repo.remote(remote)
            refspec = f"refs/heads/{branch}:refs/heads/{branch}"
            push_args = [refspec]
            if force:
                push_args.insert(0, "--force")
            remote_obj.push(push_args)
            logger.success(f"✅ Pushed branch: {branch}")
            return True
        except Exception as e:
            logger.error(f"git push failed: {e}")
            # Fallback: use subprocess
            return self._subprocess_push(branch, remote, force)

    def _subprocess_push(self, branch: str, remote: str, force: bool = False) -> bool:
        """Fallback git push via subprocess."""
        force_flag = "--force" if force else ""
        cmd = f"git push {remote} {branch} {force_flag} --set-upstream"
        result = subprocess.run(cmd, shell=True, cwd=self.project_root,
                                capture_output=True, text=True)
        if result.returncode == 0:
            logger.success(f"✅ Pushed via subprocess: {branch}")
            return True
        logger.error(f"subprocess push failed: {result.stderr}")
        return False

    # ── Remote GitHub Operations ───────────────────────────────

    def create_github_repo(
        self,
        repo_name: str,
        description: str = "",
        private: bool = False,
        auto_init: bool = False,
    ) -> Optional[RepoInfo]:
        """Create a new GitHub repository."""
        if not self._user:
            logger.error("GitHub not authenticated")
            return None
        try:
            # Check if repo already exists
            try:
                existing = self._user.get_repo(repo_name)
                logger.warning(f"Repo already exists: {existing.html_url}")
                return RepoInfo(
                    name=existing.name,
                    full_name=existing.full_name,
                    url=existing.html_url,
                    clone_url=existing.clone_url,
                    ssh_url=existing.ssh_url,
                )
            except GithubException:
                pass

            repo = self._user.create_repo(
                name=repo_name,
                description=description,
                private=private,
                auto_init=auto_init,
            )
            info = RepoInfo(
                name=repo.name,
                full_name=repo.full_name,
                url=repo.html_url,
                clone_url=repo.clone_url,
                ssh_url=repo.ssh_url,
            )
            logger.success(f"✅ GitHub repo created: {repo.html_url}")
            return info
        except GithubException as e:
            logger.error(f"create_github_repo failed: {e}")
            return None

    def create_release(
        self,
        repo_name: str,
        tag: str = "v1.0.0",
        name: str = "Initial Release",
        body: str = "🚀 First release generated by Project TITAN",
    ) -> Optional[str]:
        """Create a GitHub release."""
        if not self._user:
            return None
        try:
            repo = self._user.get_repo(repo_name)
            release = repo.create_git_release(
                tag=tag,
                name=name,
                message=body,
                draft=False,
                prerelease=False,
            )
            logger.success(f"✅ Release created: {release.html_url}")
            return release.html_url
        except Exception as e:
            logger.error(f"create_release failed: {e}")
            return None

    def create_issue(self, repo_name: str, title: str, body: str, labels: list[str] | None = None) -> Optional[str]:
        """Create a GitHub issue."""
        if not self._user:
            return None
        try:
            repo = self._user.get_repo(repo_name)
            issue = repo.create_issue(title=title, body=body, labels=labels or [])
            logger.info(f"Issue created: #{issue.number} — {title}")
            return issue.html_url
        except Exception as e:
            logger.error(f"create_issue failed: {e}")
            return None

    # ── Full Pipeline ─────────────────────────────────────────

    def full_push_pipeline(
        self,
        repo_name: str,
        commit_message: str = "🤖 Generated by Project TITAN",
        description: str = "",
        branches: list[str] | None = None,
        private: bool = False,
    ) -> dict:
        """
        Complete GitHub push pipeline:
        1. git init
        2. Create GitHub repo
        3. Set remote
        4. git add + commit
        5. Push main + extra branches
        6. Create release

        Returns: dict with status and repo URL
        """
        results = {
            "success": False,
            "repo_url": "",
            "branches_pushed": [],
            "release_url": "",
            "errors": [],
        }

        # 1. Init git
        if not self.git_init():
            results["errors"].append("git init failed")
            return results

        # 2. Stage + commit
        self.git_add_all()
        if not self.git_commit(commit_message):
            results["errors"].append("git commit failed")
            return results

        # 3. Create GitHub repo
        repo_info = self.create_github_repo(
            repo_name=repo_name,
            description=description,
            private=private,
        )
        if not repo_info:
            results["errors"].append("Failed to create GitHub repo")
            return results

        results["repo_url"] = repo_info.url

        # 4. Set remote using token-auth URL
        remote_url = f"https://{self._username}:{GITHUB_TOKEN}@github.com/{self._username}/{repo_name}.git"
        self.set_remote(remote_url)

        # 5. Push main
        if self.git_push("main"):
            results["branches_pushed"].append("main")
        else:
            # Try master
            if self.git_push("master"):
                results["branches_pushed"].append("master")

        # 6. Push extra branches
        for branch in (branches or ["develop"]):
            try:
                self.create_branch(branch)
                self.git_push(branch)
                self.checkout_branch("main")
                results["branches_pushed"].append(branch)
            except Exception as e:
                results["errors"].append(f"Branch {branch}: {e}")

        # 7. Create release
        release_url = self.create_release(repo_name=repo_name)
        if release_url:
            results["release_url"] = release_url

        results["success"] = bool(results["branches_pushed"])
        return results

    @property
    def username(self) -> str:
        return self._username or "unknown"
